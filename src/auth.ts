import { query } from './utils/helpers';

export async function createUser(email: string, password: string) {
  // SQL injection vulnerability
  const sql = `INSERT INTO users (email, password) VALUES ('${email}', '${password}')`;
  return query(sql);
}

export async function getUser(id: number) {
  const sql = `SELECT * FROM users WHERE id = ${id}`;
  return query(sql);
}
