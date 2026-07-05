export async function query(sql: string) {
  // Mock DB query
  return { data: 'mock' };
}

export function formatDate(date: Date) {
  return date.toISOString();
}
