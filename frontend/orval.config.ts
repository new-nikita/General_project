// orval.config.ts для Orval v8+
export default {
  usersApi: {
    input: 'http://localhost:8000/openapi.json', // путь к OpenAPI FastAPI
    output: {
      target: './src/api/generated/users.ts',   // куда Orval будет писать функции
      client: 'axios',                          // используем axios
      mode: 'tags-split',                        // создаёт файлы по тегам
    }
  }
}