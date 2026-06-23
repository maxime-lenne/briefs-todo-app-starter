import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { api } from '../src/lib/api';
import type { Todo } from '../src/lib/types';

const sampleTodo: Todo = {
	id: 1,
	title: 'Buy milk',
	description: null,
	completed: false,
	created_at: '2026-04-30T10:00:00Z',
	updated_at: null
};

function jsonResponse(body: unknown, init: ResponseInit = { status: 200 }): Response {
	return new Response(JSON.stringify(body), {
		...init,
		headers: { 'Content-Type': 'application/json', ...(init.headers ?? {}) }
	});
}

describe('api client', () => {
	let fetchMock: ReturnType<typeof vi.fn>;

	beforeEach(() => {
		fetchMock = vi.fn();
		vi.stubGlobal('fetch', fetchMock);
	});

	afterEach(() => {
		vi.unstubAllGlobals();
	});

	it('listTodos calls GET /todos and returns the parsed body', async () => {
		fetchMock.mockResolvedValue(jsonResponse([sampleTodo]));

		const todos = await api.listTodos();

		expect(fetchMock).toHaveBeenCalledTimes(1);
		const [url, init] = fetchMock.mock.calls[0];
		expect(url).toBe('/api/todos');
		expect(init?.method).toBeUndefined();
		expect(todos).toEqual([sampleTodo]);
	});

	it('createTodo POSTs the payload as JSON', async () => {
		fetchMock.mockResolvedValue(jsonResponse(sampleTodo, { status: 201 }));

		const created = await api.createTodo({ title: 'Buy milk' });

		const [url, init] = fetchMock.mock.calls[0];
		expect(url).toBe('/api/todos');
		expect(init?.method).toBe('POST');
		expect(init?.body).toBe(JSON.stringify({ title: 'Buy milk' }));
		expect((init?.headers as Record<string, string>)['Content-Type']).toBe('application/json');
		expect(created).toEqual(sampleTodo);
	});

	it('updateTodo PUTs to /todos/:id', async () => {
		fetchMock.mockResolvedValue(jsonResponse({ ...sampleTodo, completed: true }));

		await api.updateTodo(1, { completed: true });

		const [url, init] = fetchMock.mock.calls[0];
		expect(url).toBe('/api/todos/1');
		expect(init?.method).toBe('PUT');
		expect(init?.body).toBe(JSON.stringify({ completed: true }));
	});

	it('deleteTodo handles 204 No Content', async () => {
		fetchMock.mockResolvedValue(new Response(null, { status: 204 }));

		await expect(api.deleteTodo(1)).resolves.toBeUndefined();

		const [url, init] = fetchMock.mock.calls[0];
		expect(url).toBe('/api/todos/1');
		expect(init?.method).toBe('DELETE');
	});

	it('throws when the response is not ok', async () => {
		fetchMock.mockResolvedValue(
			new Response('boom', { status: 500, statusText: 'Internal Server Error' })
		);

		await expect(api.listTodos()).rejects.toThrow(/500/);
	});
});
