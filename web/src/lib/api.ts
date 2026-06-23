import { env } from '$env/dynamic/public';
import type { Todo, TodoCreate, TodoUpdate } from './types';

const BASE = env.PUBLIC_API_BASE || '/api';

async function request<T>(path: string, init?: RequestInit): Promise<T> {
	const res = await fetch(`${BASE}${path}`, {
		headers: { 'Content-Type': 'application/json' },
		...init
	});
	if (!res.ok) {
		const detail = await res.text().catch(() => res.statusText);
		throw new Error(`${res.status} ${res.statusText}: ${detail}`);
	}
	if (res.status === 204) return undefined as T;
	return res.json() as Promise<T>;
}

export const api = {
	listTodos: () => request<Todo[]>('/todos'),
	getTodo: (id: number) => request<Todo>(`/todos/${id}`),
	createTodo: (payload: TodoCreate) =>
		request<Todo>('/todos', { method: 'POST', body: JSON.stringify(payload) }),
	updateTodo: (id: number, payload: TodoUpdate) =>
		request<Todo>(`/todos/${id}`, { method: 'PUT', body: JSON.stringify(payload) }),
	deleteTodo: (id: number) => request<void>(`/todos/${id}`, { method: 'DELETE' })
};
