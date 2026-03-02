import { Pool } from 'pg';

const pool = new Pool({
    user: process.env.DB_USER || 'postgres',
    password: process.env.DB_PASS || 'root',
    host: process.env.DB_HOST || 'localhost',
    port: parseInt(process.env.DB_PORT || '5432'),
    database: process.env.DB_NAME || 'alpha',
    max: 10,
    idleTimeoutMillis: 30000,
    connectionTimeoutMillis: 5000,
});

export async function query<T = Record<string, unknown>>(
    sql: string,
    params?: unknown[]
): Promise<T[]> {
    const client = await pool.connect();
    try {
        const result = await client.query(sql, params);
        return result.rows as T[];
    } finally {
        client.release();
    }
}

export default pool;
