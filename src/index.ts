import { createUser, getUser } from './auth';
import { processData } from './data';

async function main() {
  const user = await createUser('alice@example.com', 'password123');
  const data = await processData(user.id);
  console.log(data);
}
main();
