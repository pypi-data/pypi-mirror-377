"""Core computational verification and algorithm validation tests.

(AI generated docstring)

This module validates the mathematical correctness of map folding computations and
serves as the primary testing ground for new computational approaches. It's the most
important module for users who create custom folding algorithms or modify existing ones.

The tests here verify that different computational flows produce identical results,
ensuring mathematical consistency across implementation strategies. This is critical
for maintaining confidence in results as the codebase evolves and new optimization
techniques are added.

Key Testing Areas:
- Flow control validation across different algorithmic approaches
- OEIS sequence value verification against known mathematical results
- Code generation and execution for dynamically created computational modules
- Numerical accuracy and consistency checks

For users implementing new computational methods: use the `test_flowControl` pattern
as a template. It demonstrates how to validate that your algorithm produces results
consistent with the established mathematical foundation.

The `test_writeJobNumba` function shows how to test dynamically generated code,
which is useful if you're working with the code synthesis features of the package.
"""

from mapFolding import countFolds, dictionaryOEISMapFolding, dictionaryOEISMeanders, getFoldsTotalKnown, oeisIDfor_n
from mapFolding.algorithms import oeisIDbyFormula
from mapFolding.dataBaskets import MapFoldingState
from mapFolding.someAssemblyRequired.RecipeJob import RecipeJobTheorem2
from mapFolding.someAssemblyRequired.toolkitNumba import parametersNumbaLight
from mapFolding.syntheticModules.initializeState import transitionOnGroupsOfFolds
from mapFolding.tests.conftest import registrarRecordsTemporaryFilesystemObject, standardizedEqualToCallableReturn
from pathlib import Path, PurePosixPath
from typing import TYPE_CHECKING
import importlib.util
import multiprocessing
import pytest

if TYPE_CHECKING:
	from collections.abc import Callable

if __name__ == '__main__':
	multiprocessing.set_start_method('spawn')

def test_aOFn_calculate_value_mapFolding(oeisID: str) -> None:
	"""Verify OEIS sequence value calculations against known reference values.

	Tests the `oeisIDfor_n` function by comparing its calculated output against
	known correct values from the OEIS database. This ensures that sequence
	value computations remain mathematically accurate across code changes.

	The test iterates through validation test cases defined in `settingsOEIS`
	for the given OEIS sequence identifier, verifying that each computed value
	matches its corresponding known reference value.

	Parameters
	----------
	oeisID : str
		The OEIS sequence identifier to test calculations for.

	"""
	for n in dictionaryOEISMapFolding[oeisID]['valuesTestValidation']:
		standardizedEqualToCallableReturn(dictionaryOEISMapFolding[oeisID]['valuesKnown'][n], oeisIDfor_n, oeisID, n)

def test_aOFn_calculate_value_meanders(oeisIDMeanders: str) -> None:
	"""Verify Meanders OEIS sequence value calculations against known reference values.

	Tests the functions in `mapFolding.algorithms.oeisIDbyFormula` by comparing their
	calculated output against known correct values from the OEIS database for Meanders IDs.

	Parameters
	----------
	oeisIDMeanders : str
		The Meanders OEIS sequence identifier to test calculations for.

	"""
	oeisIDcallable: Callable[[int], int] = getattr(oeisIDbyFormula, oeisIDMeanders)
	for n in dictionaryOEISMeanders[oeisIDMeanders]['valuesTestValidation']:
		standardizedEqualToCallableReturn(
			dictionaryOEISMeanders[oeisIDMeanders]['valuesKnown'][n],
			oeisIDcallable,
			n,
		)

@pytest.mark.parametrize('flow', ['daoOfMapFolding', 'numba', 'theorem2', 'theorem2Numba', 'theorem2Trimmed'])
def test_flowControl(mapShapeTestCountFolds: tuple[int, ...], flow: str) -> None:
	"""Validate that different computational flows produce valid results.

	(AI generated docstring)

	This is the primary test for ensuring mathematical consistency across different
	algorithmic implementations. When adding a new computational approach, include
	it in the parametrized flow list to verify it produces correct results.

	The test compares the output of each flow against known correct values from
	OEIS sequences, ensuring that optimization techniques don't compromise accuracy.

	Parameters
	----------
	mapShapeTestCountFolds : tuple[int, ...]
		The map shape dimensions to test fold counting for.
	flow : str
		The computational flow algorithm to validate.

	"""
	standardizedEqualToCallableReturn(getFoldsTotalKnown(mapShapeTestCountFolds), countFolds, None, None, None, None, mapShapeTestCountFolds, None, None, flow)

@pytest.mark.parametrize('flow', ['daoOfMapFolding', 'numba', 'theorem2', 'theorem2Numba', 'theorem2Trimmed'])
def test_flowControlByOEISid(oeisID: str, flow: str) -> None:
	"""Validate that different flow paths using oeisID produce valid results.

	Parameters
	----------
	oeisID : str
		The OEIS sequence identifier to test.
	flow : str
		The computational flow algorithm to validate.

	"""
	listDimensions = None
	pathLikeWriteFoldsTotal = None
	computationDivisions = None
	CPUlimit = None
	mapShape = None

	oeis_n = 2
	for oeis_n in dictionaryOEISMapFolding[oeisID]['valuesTestValidation']:
		if oeis_n < 2:
			continue

		if oeisID in dictionaryOEISMeanders:
			expected = dictionaryOEISMeanders[oeisID]['valuesKnown'][oeis_n]
		else:
			expected = dictionaryOEISMapFolding[oeisID]['valuesKnown'][oeis_n]

		standardizedEqualToCallableReturn(
			expected
			, countFolds, listDimensions, pathLikeWriteFoldsTotal, computationDivisions, CPUlimit, mapShape
			, oeisID, oeis_n, flow)

@pytest.mark.parametrize('pathFilename_tmpTesting', ['.py'], indirect=True)
def test_writeJobNumba(oneTestCuzTestsOverwritingTests: tuple[int, ...], pathFilename_tmpTesting: Path) -> None:
	"""Test dynamic code generation and execution for computational modules.

	(AI generated docstring)

	This test validates the package's ability to generate, compile, and execute
	optimized computational code at runtime. It's essential for users working with
	the code synthesis features or implementing custom optimization strategies.

	The test creates a complete computational module, executes it, and verifies
	that the generated code produces mathematically correct results. This pattern
	can be adapted for testing other dynamically generated computational approaches.

	Parameters
	----------
	oneTestCuzTestsOverwritingTests : tuple[int, ...]
		The map shape dimensions for testing code generation.
	pathFilename_tmpTesting : Path
		The temporary file path for generated module testing.

	"""
	from mapFolding.someAssemblyRequired.makeJobTheorem2Numba import makeJobNumba  # noqa: PLC0415
	from mapFolding.someAssemblyRequired.toolkitNumba import SpicesJobNumba  # noqa: PLC0415
	mapShape = oneTestCuzTestsOverwritingTests
	state = transitionOnGroupsOfFolds(MapFoldingState(mapShape))

	pathFilenameModule = pathFilename_tmpTesting.absolute()
	pathFilenameFoldsTotal = pathFilenameModule.with_suffix('.foldsTotalTesting')
	registrarRecordsTemporaryFilesystemObject(pathFilenameFoldsTotal)

	jobTest = RecipeJobTheorem2(state
						, pathModule=PurePosixPath(pathFilenameModule.parent)
						, moduleIdentifier=pathFilenameModule.stem
						, pathFilenameFoldsTotal=PurePosixPath(pathFilenameFoldsTotal))
	spices = SpicesJobNumba(useNumbaProgressBar=False, parametersNumba=parametersNumbaLight)
	makeJobNumba(jobTest, spices)

	Don_Lapre_Road_to_Self_Improvement = importlib.util.spec_from_file_location("__main__", pathFilenameModule)
	if Don_Lapre_Road_to_Self_Improvement is None:
		message = f"Failed to create module specification from {pathFilenameModule}"
		raise ImportError(message)
	if Don_Lapre_Road_to_Self_Improvement.loader is None:
		message = f"Failed to get loader for module {pathFilenameModule}"
		raise ImportError(message)
	module = importlib.util.module_from_spec(Don_Lapre_Road_to_Self_Improvement)

	module.__name__ = "__main__"
	Don_Lapre_Road_to_Self_Improvement.loader.exec_module(module)

	standardizedEqualToCallableReturn(str(getFoldsTotalKnown(oneTestCuzTestsOverwritingTests)), pathFilenameFoldsTotal.read_text(encoding="utf-8").strip)
