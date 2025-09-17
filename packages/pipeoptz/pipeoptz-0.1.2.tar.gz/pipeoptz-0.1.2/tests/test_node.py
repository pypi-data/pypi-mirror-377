import pytest
import numpy as np
from unittest.mock import Mock

import sys, os
sys.path.append(os.path.abspath("../src/"))
from pipeoptz.node import Node, NodeIf, NodeFor, NodeWhile
from pipeoptz.pipeline import Pipeline


@pytest.fixture
def simple_add_func():
    """
    A simple function that adds two numbers.
    """
    return lambda a, b: a + b

@pytest.fixture
def mock_func_with_call_tracker():
    """
    A mock function that tracks its calls.
    """
    mock = Mock(return_value="computed")
    return mock

@pytest.fixture
def true_pipeline():
    """
    A simple pipeline for the 'true' path of NodeIf.
    """
    p = Pipeline(name="true_path")
    p.add_node(Node(id="true_node", func=lambda x: f"true_{x}"), predecessors={'x': 'run_params:input'})
    return p

@pytest.fixture
def false_pipeline():
    """
    A simple pipeline for the 'false' path of NodeIf.
    """
    p = Pipeline(name="false_path")
    p.add_node(Node(id="false_node", func=lambda x: f"false_{x}"), predecessors={'x': 'run_params:input'})
    return p

@pytest.fixture
def loop_pipeline():
    """
    A simple pipeline for loop nodes.
    """
    p = Pipeline(name="loop_pipe")
    p.add_node(Node(id="add_one", func=lambda loop_var: loop_var + 1), predecessors={'loop_var': 'run_params:loop_var'})
    return p


# --- Class Node tests ---

class TestNode:
    def test_node_initialization(self, simple_add_func):
        """
        Tests if a Node is initialized correctly.
        """
        node = Node(id="add_node", func=simple_add_func, fixed_params={'a': 1})
        assert node.id == "add_node"
        assert node.func == simple_add_func
        assert node.fixed_params == {'a': 1}
        assert node.output is None
        assert node.input_hash_last_exec is None

    def test_get_id(self, simple_add_func):
        """
        Tests the get_id method.
        """
        node = Node(id="test_id", func=simple_add_func)
        assert node.get_id() == "test_id"

    def test_execute_simple(self, simple_add_func):
        """
        Tests that the basic execution without fixed parameters works correctly.
        """
        node = Node(id="add_node", func=simple_add_func)
        result = node.execute(inputs={'a': 5, 'b': 10})
        assert result == 15

    def test_execute_with_fixed_params(self, simple_add_func):
        """
        Tests execution with a mix of fixed and runtime parameters.
        """
        node = Node(id="add_node", func=simple_add_func, fixed_params={'a': 1})
        result = node.execute(inputs={'b': 9})
        assert result == 10

    def test_memory_caching_avoids_recomputation(self, mock_func_with_call_tracker):
        """
        Tests that memory=True prevents re-execution with the same inputs.
        """
        node = Node(id="cache_node", func=mock_func_with_call_tracker)
        
        result1 = node.execute(inputs={'x': 1})
        assert result1 == "computed"
        assert mock_func_with_call_tracker.call_count == 1
        assert node.output == "computed"

        result2 = node.execute(inputs={'x': 1})
        assert result2 == "computed"
        assert mock_func_with_call_tracker.call_count == 1

    def test_memory_caching_recomputes_on_new_input(self, mock_func_with_call_tracker):
        """
        Tests that memory=True re-executes with different inputs.
        """
        node = Node(id="cache_node", func=mock_func_with_call_tracker)
        node.execute(inputs={'x': 1})
        assert mock_func_with_call_tracker.call_count == 1
        node.execute(inputs={'x': 2})
        assert mock_func_with_call_tracker.call_count == 2

    def test_memory_caching_with_numpy_array(self):
        """
        Tests caching with numpy arrays as input.
        """
        call_count = 0
        def numpy_func(arr):
            nonlocal call_count
            call_count += 1
            return np.sum(arr)

        node = Node(id="numpy_node", func=numpy_func)
        arr1 = np.array([1, 2, 3])
        arr2 = np.array([4, 5, 6])

        res1 = node.execute(inputs={'arr': arr1})
        assert res1 == 6
        assert call_count == 1

        res2 = node.execute(inputs={'arr': arr1})
        assert res2 == 6
        assert call_count == 1

        res3 = node.execute(inputs={'arr': np.array([1, 2, 3])})
        assert res3 == 6
        assert call_count == 1

        res4 = node.execute(inputs={'arr': arr2})
        assert res4 == 15
        assert call_count == 2

    def test_clear_memory(self, mock_func_with_call_tracker):
        """
        Tests that clear_memory forces re-execution.
        """
        node = Node(id="cache_node", func=mock_func_with_call_tracker)
        
        node.execute(inputs={'x': 1})
        assert mock_func_with_call_tracker.call_count == 1
        
        node.clear_memory()
        assert node.output is None
        assert node.input_hash_last_exec is None

        node.execute(inputs={'x': 1})
        assert mock_func_with_call_tracker.call_count == 2

    def test_set_fixed_param(self, simple_add_func):
        """
        Tests setting a single fixed parameter.
        """
        node = Node(id="add_node", func=simple_add_func, fixed_params={'a': 1})
        node.set_fixed_param('a', 5)
        assert node.get_fixed_params()['a'] == 5

    def test_set_fixed_param_raises_error_for_new_key(self, simple_add_func):
        """
        Tests that setting a non-existent fixed parameter raises a ValueError.
        """
        node = Node(id="add_node", func=simple_add_func, fixed_params={'a': 1})
        with pytest.raises(ValueError, match="Key 'b' is not a fixed parameter of node 'add_node'"):
            node.set_fixed_param('b', 10)

    def test_is_fixed_param(self, simple_add_func):
        """
        Tests the is_fixed_param method.
        """
        node = Node(id="add_node", func=simple_add_func, fixed_params={'a': 1})
        assert node.is_fixed_param('a') is True
        assert node.is_fixed_param('b') is False


# --- Class NodeIf tests ---

class TestNodeIf:
    def test_nodeif_initialization(self, true_pipeline, false_pipeline):
        """
        Tests if a NodeIf is initialized correctly.
        """
        cond_func = lambda x: x > 0
        node_if = NodeIf(
            id="if_node",
            condition_func=cond_func,
            true_pipeline=true_pipeline,
            false_pipeline=false_pipeline,
            fixed_params={'y': 1}
        )
        assert node_if.id == "if_node"
        assert node_if.func == cond_func
        assert node_if.true_pipeline == true_pipeline
        assert node_if.false_pipeline == false_pipeline
        assert node_if.fixed_params == {'y': 1}

    def test_execute_true_path(self, true_pipeline, false_pipeline):
        """
        Tests that the 'true' pipeline is executed if the condition is true.
        """
        cond_func = lambda val: val > 10
        node_if = NodeIf(
            id="if_node",
            condition_func=cond_func,
            true_pipeline=true_pipeline,
            false_pipeline=false_pipeline
        )
        
        inputs = {'condition_func:val': 20, 'input': 'world'}
        result = node_if.execute(inputs=inputs)
        
        assert result == "true_world"

    def test_execute_false_path(self, true_pipeline, false_pipeline):
        """
        Tests that the 'false' pipeline is executed if the condition is false.
        """
        cond_func = lambda val: val > 10
        node_if = NodeIf(
            id="if_node",
            condition_func=cond_func,
            true_pipeline=true_pipeline,
            false_pipeline=false_pipeline
        )
        
        inputs = {'condition_func:val': 5, 'input': 'space'}
        result = node_if.execute(inputs=inputs)
        
        assert result == "false_space"

    def test_get_fixed_params_nested(self, true_pipeline, false_pipeline):
        """
        Tests retrieving fixed parameters from NodeIf and its sub-pipelines.
        """
        true_pipeline.get_node("true_node").fixed_params = {'z': 100}
        
        node_if = NodeIf(
            id="if_node",
            condition_func=lambda: True,
            true_pipeline=true_pipeline,
            false_pipeline=false_pipeline,
            fixed_params={'own_param': 42}
        )
        
        params = node_if.get_fixed_params()
        
        expected_params = {
            'own_param': 42,
            'true_pipeline': {'true_node.z': 100},
            'false_pipeline': {}
        }
        assert params == expected_params

    def test_set_fixed_params_nested(self, true_pipeline, false_pipeline):
        """
        Tests setting fixed parameters on NodeIf and its sub-pipelines.
        """
        true_pipeline.get_node("true_node").fixed_params = {'z': 0}
        false_pipeline.get_node("false_node").fixed_params = {'w': 0}

        node_if = NodeIf(
            id="if_node",
            condition_func=lambda: True,
            true_pipeline=true_pipeline,
            false_pipeline=false_pipeline,
            fixed_params={'own_param': 0}
        )

        new_params = {
            'own_param': 99,
            'true_pipeline': {'true_node.z': 101},
            'false_pipeline': {'false_node.w': 202}
        }
        
        node_if.set_fixed_params(new_params)

        assert node_if.fixed_params['own_param'] == 99
        assert true_pipeline.get_node("true_node").fixed_params['z'] == 101
        assert false_pipeline.get_node("false_node").fixed_params['w'] == 202


# --- Class NodeFor tests ---

class TestNodeFor:
    def test_nodefor_initialization(self, loop_pipeline):
        """
        Tests if a NodeFor is initialized correctly.
        """
        node_for = NodeFor(id="for_node", loop_pipeline=loop_pipeline, fixed_params={'iterations': 3})
        assert node_for.id == "for_node"
        assert node_for.loop_pipeline == loop_pipeline
        assert node_for.fixed_params == {'iterations': 3}

    def test_execute_fixed_iterations(self, loop_pipeline):
        """
        Tests NodeFor execution with a fixed number of iterations.
        """
        node_for = NodeFor(id="for_node", loop_pipeline=loop_pipeline, fixed_params={'iterations': 3})
        result = node_for.execute(inputs={'loop_var': 0})
        assert result == 3

    def test_execute_input_iterations(self, loop_pipeline):
        """
        Tests NodeFor execution with iterations from input.
        """
        node_for = NodeFor(id="for_node", loop_pipeline=loop_pipeline)
        result = node_for.execute(inputs={'iterations': 5, 'loop_var': 0})
        assert result == 5

    def test_execute_missing_iterations_raises_error(self, loop_pipeline):
        """
        Tests that NodeFor raises an error if 'iterations' is missing.
        """
        node_for = NodeFor(id="for_node", loop_pipeline=loop_pipeline)
        with pytest.raises(ValueError, match="NodeFor requires an 'iterations' input"):
            node_for.execute(inputs={'loop_var': 0})

    def test_execute_missing_loop_var_raises_error(self, loop_pipeline):
        """
        Tests that NodeFor raises an error if 'loop_var' is missing.
        """
        node_for = NodeFor(id="for_node", loop_pipeline=loop_pipeline, fixed_params={'iterations': 3})
        with pytest.raises(ValueError, match="NodeFor requires a 'loop_var' input"):
            node_for.execute(inputs={})


# --- Class NodeWhile tests ---

class TestNodeWhile:
    def test_nodewhile_initialization(self, loop_pipeline):
        """
        Tests if a NodeWhile is initialized correctly.
        """
        cond_func = lambda loop_var: loop_var < 5
        node_while = NodeWhile(id="while_node", condition_func=cond_func, loop_pipeline=loop_pipeline)
        assert node_while.id == "while_node"
        assert node_while.func == cond_func
        assert node_while.loop_pipeline == loop_pipeline

    def test_execute_while_condition_true(self, loop_pipeline):
        """
        Tests NodeWhile execution until the condition is false.
        """
        cond_func = lambda loop_var: loop_var < 5
        node_while = NodeWhile(id="while_node", condition_func=cond_func, loop_pipeline=loop_pipeline)
        result = node_while.execute(inputs={'loop_var': 0})
        assert result == 5

    def test_execute_max_iterations(self, loop_pipeline):
        """
        Tests NodeWhile execution with a max_iterations limit.
        """
        cond_func = lambda loop_var: True  # Condition is always true
        node_while = NodeWhile(id="while_node", condition_func=cond_func, loop_pipeline=loop_pipeline, fixed_params={'max_iterations': 3})
        result = node_while.execute(inputs={'loop_var': 0})
        assert result == 3

    def test_execute_missing_loop_var_raises_error(self, loop_pipeline):
        """
        Tests that NodeWhile raises an error if 'loop_var' is missing.
        """
        cond_func = lambda loop_var: loop_var < 5
        node_while = NodeWhile(id="while_node", condition_func=cond_func, loop_pipeline=loop_pipeline)
        with pytest.raises(ValueError, match="NodeWhile requires a 'loop_var' input"):
            node_while.execute(inputs={})