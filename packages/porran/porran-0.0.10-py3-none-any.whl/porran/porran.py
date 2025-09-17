import os
from time import time
from typing import Callable, List, Optional, Union

import numpy as np
from pymatgen.core import Structure
from pymatgen.io.cif import CifParser

from .create_structure import create_dmof, create_zeo
from .get_zeolite import get_zeolite
from .graph_creation import radius_graph, zeo_graph
from .mask_method import (
    mask_all,
    mask_array,
    mask_box,
    mask_combination,
    mask_h_on_c,
    mask_species,
    mask_zeo,
)
from .replacement_algorithms import (
    multi_clusters,
    chains, 
    clusters, 
    maximize_entropy, 
    random, 
    random_lowenstein,
    lowenstein,
)
from .utils import is_atom, write_cif


class PORRAN:

    def __init__(
        self,
        cif_path: Optional[str] = None,
        graph_method: Optional[Union[str, Callable]] = None,
        mask_method: Optional[Union[List[str], np.array, str]] = None,
        seed: Optional[int] = None,
        *args,
        **kwargs,
    ):

        if cif_path is not None:
            self.init_structure(cif_path, graph_method, mask_method, *args, **kwargs)
        if seed is not None:
            self.set_seed(seed)

    def init_structure(
        self,
        cif_path: str,
        graph_method: Union[str, Callable],
        mask_method: Optional[Union[List[str], np.array, str]] = None,
        check_cif: bool = False, site_tolerance: float = 1e-3,
        *args,
        **kwargs,
    ):
        """
        Initialize the structure and the method to build the graph

        Parameters
        ----------
        cif_path : str
            Path to the cif file
        graph_method : Union[str, Callable]
            Method to build the graph. If str, it can be 'zeolite' or 'radius'
        mask_method : Optional[Union[List[str], np.array]]
            Method to select atoms to include in the graph.
            To directly select atoms, its possible to provide an np.array with the indices of the atoms to include set to 1
            To select atoms by species, provide a list of species to include
        check_cif : bool, optional
            Check the cif file for errors, default is False
        site_tolerance : float, optional
            Tolerance for site matching, default is 1e-3
    
        Returns
        -------
        None
        """
        # name is the name of the cif file
        self.name = cif_path.split("/")[-1].split(".")[0]
        self.structure = self._read_structure(cif_path, check_cif)
        self.graph_method = self._get_graph_method(graph_method)
        self.mask_method = self._get_mask_method(mask_method)
        self.mask = self.mask_method(self.structure, mask_method, *args, **kwargs)
        self.structure_graph = self.graph_method(
            self.structure, mask=self.mask, *args, **kwargs
        )

    def from_IZA_code(
        self,
        zeolite_code: str,
        graph_method: Union[str, Callable],
        mask_method: Optional[Union[List[str], np.array, str]] = None,
        *args,
        **kwargs,
    ):
        """
        Initialize the structure from an IZA code

        Parameters
        ----------
        zeolite_code : str
            IZA code of the zeolite
        graph_method : Union[str, Callable]
            Method to build the graph. If str, it can be 'zeolite' or 'radius'
        mask_method : Optional[Union[List[str], np.array]]
            Method to select atoms to include in the graph.
            To directly select atoms, its possible to provide an np.array with the indices of the atoms to include set to 1
            To select atoms by species, provide a list of species to include

        Returns
        -------
        None
        """
        self.name = zeolite_code
        self.structure = get_zeolite(zeolite_code)
        self.graph_method = self._get_graph_method(graph_method)
        self.mask_method = self._get_mask_method(mask_method)
        self.mask = self.mask_method(self.structure, mask_method, *args, **kwargs)
        self.structure_graph = self.graph_method(
            self.structure, mask=self.mask, *args, **kwargs
        )

    def change_graph_method(
        self,
        graph_method: Union[str, Callable],
        mask_method: Optional[Union[List[str], np.array, str]] = None,
        *args,
        **kwargs,
    ):
        """
        Change the method to build the graph

        Parameters
        ----------
        graph_method : Union[str, Callable]
            Method to build the graph. If str, it can be 'zeolite' or 'radius'
        mask_method : Optional[Union[List[str], np.array]]
            Method to select atoms to include in the graph.
            To directly select atoms, its possible to provide an np.array with the indices of the atoms to include set to 1
            To select atoms by species, provide a list of species to include
        Returns
        -------
        None
        """
        self.graph_method = self._get_graph_method(graph_method)
        self.mask_method = self._get_mask_method(mask_method)
        self.mask = self.mask_method(self.structure, mask_method, *args, **kwargs)
        self.structure_graph = self.graph_method(
            self.structure, mask=self.mask, *args, **kwargs
        )

    def generate_structures(
        self,
        n_structures: int,
        replace_algo: Union[str, Callable],
        create_algo: Union[str, Callable],
        n_subs: int,
        max_tries: int = 100,
        post_algo: Optional[Callable] = None,
        write: bool = False, overwrite_ok = False,
        writepath: Optional[str] = "structures",
        verbose: bool = True,
        print_error : bool = False,
        *args,
        **kwargs,
    ) -> List[Structure]:
        """
        Generate structures by replacing nodes in the graph

        Parameters
        ----------
        n_structures : int
            Number of structures to generate
        replace_algo : Union[str, Callable]
            Algorithm to select nodes to replace. If str, it can be 'random', 'random_lowenstein', 'lowenstein', 'clusters', 'multi_clusters','chains' or 'maximize_entropy'
        create_algo : Union[str, Callable]
            Algorithm to create the new structure. If str, it can be 'zeolite'
        n_subs : int
            Number of nodes to replace
        max_tries : int, optional
            Maximum number of tries to replace nodes, default is 100
        post_algo : Callable, optional
            Post processing algorithm to apply to the new structure
        write : bool, optional
            Write the structures to a file, default is False
        writepath : str, optional
            Path to write the structures to, default is None
            If writepath is not specified, a folder named 'structures' will be created in the current directory
        verbose : bool, optional
            Whether to provide information about the generation process, default is True

        Returns
        -------
        List[Structure]
            List of generated structures
        """

        if write:
            if not os.path.exists(writepath):
                os.makedirs(writepath)
            elif not os.listdir(writepath):
                pass
            elif not overwrite_ok:
                raise ValueError(
                    f"Path {writepath} already contains files. Please provide an empty or non-existing path or set write to False."
                )

        self.replace_algo = self._get_replace_algo(replace_algo)
        self.create_algo = self._get_create_algo(create_algo)
        self.post_algo = post_algo

        structures = []

        total_failed = 0
        failed = 0

        start = time()
        for i in range(n_structures):

            # for each structure, try to replace nodes max_tries times
            for j in range(max_tries):
                try:
                    sub_array = self._replace(n_subs, *args, **kwargs)
                    break
                except Exception as e:
                    sub_array = None
                    total_failed += 1
                    if print_error:
                        print(f"Failed to generate new structure: {e}")


            # if the maximum number of tries is reached, skip the structure
            if sub_array is None:
                failed += 1
                continue

            new_structure = self.create_algo(
                self.structure, self.mask, sub_array, *args, **kwargs
            )
            if self.post_algo is not None:
                new_structure = self.post_algo(new_structure, *args, **kwargs)
            structures.extend(new_structure)
            if write:
                for j in range(len(new_structure)):
                    self._write_structure(
                        new_structure[j], writepath, i * len(new_structure) + j
                    )

        end = time()
        if verbose:
            print(
                f"Successfully generated {n_structures - failed} structures in {end - start:.3f} seconds"
            )
            print(f"Failed to generate {failed} structures")
            print(f"Failed to generate new structures {total_failed} times")
        return structures

    def _get_mask_method(self, mask_method: Optional[Union[List[str], np.array, str]]):
        if mask_method is None:
            return mask_all
        elif isinstance(mask_method, str):
            if mask_method == "zeolite":
                return mask_zeo
            elif mask_method == "h_on_c":
                return mask_h_on_c
            else:
                raise ValueError(f"Unknown mask method: {mask_method}")
        elif isinstance(mask_method, list):
            # if all elements of the list are atoms, return mask_species
            if all([type(msk) == str for msk in mask_method]) and all(
                [is_atom(species) for species in mask_method]
            ):
                return mask_species
            # otherwise, create a combination of the masks
            else:
                masks = [
                    self._get_mask_method(msk_method) for msk_method in mask_method
                ]
                return mask_combination(masks)
        elif isinstance(mask_method, np.ndarray):
            if len(mask_method.shape) == 1:
                return mask_array
            elif mask_method.shape == (3, 2):
                return mask_box
            else:
                raise ValueError("Mask array must be 1D or have shape (3,2)")
        else:
            raise ValueError("Unknown mask method")

    def _get_replace_algo(self, replace_algo: Union[str, Callable]):
        if isinstance(replace_algo, str):
            if replace_algo == "random":
                return random
            elif replace_algo == "random_lowenstein":
                return random_lowenstein
            elif replace_algo == "lowenstein":
                return lowenstein
            elif replace_algo == "clusters":
                return clusters
            elif replace_algo == "multi_clusters":
                return multi_clusters
            elif replace_algo == "chains":
                return chains
            elif replace_algo == "maximize_entropy":
                return maximize_entropy
            else:
                raise ValueError(f"Unknown replace algorithm: {replace_algo}")
        else:
            return replace_algo

    def _get_create_algo(self, create_algo: Union[str, Callable]):
        if isinstance(create_algo, str):
            if create_algo == "zeolite":
                return create_zeo
            if create_algo == "dmof":
                return create_dmof
            else:
                raise ValueError(f"Unknown create algorithm: {create_algo}")
        else:
            return create_algo

    def _write_structure(
        self, structure: Structure, writepath: Optional[str] = None, i: int = 0
    ):
        """
        Write a structure to a file

        Parameters
        ----------
        structure : Structure
            Structure to write
        writepath : str, optional
            Path to write the structure to, default is None
        i : int
            Index of the structure, default is 0

        Returns
        -------
        None
        """
        if writepath is None:
            writepath = "structures"

        write_cif(
            structure,
            filename=f"{writepath}/{self.name}_{self.replace_algo.__name__}_{i}.cif",
        )
        # structure.to(filename=f'{writepath}/{self.name}_{self.replace_algo.__name__}_{i}.cif')

    def _replace(self, n_subs: int, *args, **kwargs):
        """
        Replace n_subs nodes in the graph

        Parameters
        ----------
        n_subs : int
            Number of nodes to replace

        Returns
        -------
        np.array
            Array of selected nodes to replace
        """
        sub_array = self.replace_algo(self.structure_graph, n_subs, *args, **kwargs)
        return sub_array

    def _get_graph_method(self, graph_method: Union[str, Callable]):
        if isinstance(graph_method, str):
            if graph_method == "zeolite":
                return zeo_graph
            elif graph_method == "radius":
                return radius_graph
            else:
                raise ValueError(f"Unknown graph method: {graph_method}")
        else:
            return graph_method

    def _read_structure(self, cif_path: str, check_cif: bool = False, site_tolerance: float = 1e-3):
        """
        Read a structure from a cif file

        Parameters
        ----------
        cif_path : str
            Path to the cif file
        check_cif : bool, optional
            Check the cif file for errors, default is False

        Returns
        -------
        Structure
            Structure object of the cif file
        """
        parser = CifParser(cif_path, check_cif=check_cif, site_tolerance=site_tolerance)
        structure = parser.parse_structures(primitive=False)[0]
        return structure

    def __repr__(self):
        return f"PORRAN(cif_path={self.cif_path}, graph_method={self.graph_method}, mask_method={self.mask_method})"

    def __str__(self):
        return f"PORRAN(cif_path={self.cif_path}, graph_method={self.graph_method}, mask_method={self.mask_method})"

    def set_seed(self, seed: int):
        np.random.seed(seed)
