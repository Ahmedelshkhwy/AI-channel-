                alert_count INTEGER NOT NULL,
                slow_count INTEGER NOT NULL,
                fast_count INTEGER NOT NULL
            );

            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                upload_id INTEGER NOT NULL,
                branch TEXT NOT NULL,
                week_date TEXT NOT NULL,
                name TEXT NOT NULL,
                category TEXT NOT NULL DEFAULT 'UNCATEGORIZED',
                sku TEXT,
                sold REAL NOT NULL,
                stock REAL NOT NULL,
                price REAL NOT NULL,
                cost_price REAL NOT NULL DEFAULT 0,
                stock_value REAL NOT NULL,
                cost_value REAL NOT NULL DEFAULT 0,
                turnover_ratio REAL NOT NULL,
