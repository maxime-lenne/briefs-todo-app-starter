import { describe, expect, it } from 'vitest';
import type { Filter, Todo } from '../src/lib/types';

function makeTodo(overrides: Partial<Todo>): Todo {
	return {
		id: 1,
		title: 'Sample',
		description: null,
		completed: false,
		created_at: '2026-04-30T10:00:00Z',
		updated_at: null,
		...overrides
	};
}

function applyFilter(todos: Todo[], filter: Filter): Todo[] {
	if (filter === 'active') return todos.filter((t) => !t.completed);
	if (filter === 'completed') return todos.filter((t) => t.completed);
	return todos;
}

describe('filter logic', () => {
	const todos = [
		makeTodo({ id: 1, title: 'a', completed: false }),
		makeTodo({ id: 2, title: 'b', completed: true }),
		makeTodo({ id: 3, title: 'c', completed: false })
	];

	it('returns all todos when filter is "all"', () => {
		expect(applyFilter(todos, 'all')).toHaveLength(3);
	});

	it('returns only active todos when filter is "active"', () => {
		const result = applyFilter(todos, 'active');
		expect(result.map((t) => t.id)).toEqual([1, 3]);
	});

	it('returns only completed todos when filter is "completed"', () => {
		const result = applyFilter(todos, 'completed');
		expect(result.map((t) => t.id)).toEqual([2]);
	});
});
