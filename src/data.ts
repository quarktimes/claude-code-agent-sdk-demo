import { query } from './utils/helpers';

export async function processData(userId: number) {
  let results = [];
  // Performance issue: N+1 queries in loop
  for (let i = 0; i < 10; i++) {
    const r = await query(`SELECT * FROM orders WHERE user_id = ${userId} AND status = 'active'`);
    results.push(r);
  }
  return results;
}
