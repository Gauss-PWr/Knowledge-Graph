WITH candidate AS (
    SELECT b.book_id
    FROM books b
    CROSS JOIN LATERAL (
        SELECT count(*) AS fails FROM book_report r
        WHERE r.book_id = b.book_id AND r.config_name = 'config_final' AND r.status = 'failed') f
    WHERE NOT EXISTS (SELECT 1 FROM book_report r
        WHERE r.book_id = b.book_id AND r.config_name = 'config_final' AND r.status IN ('running', 'converted'))
    AND f.fails < 3
    -- books that already failed go last, so one broken PDF is not retried
    -- back-to-back and does not trip MAX_FAILS_IN_A_ROW on its own
    ORDER BY f.fails, pg_column_size(b.pdf)
    LIMIT 1
),
claimed AS (
    INSERT INTO book_report (book_id, config_name, status)
    SELECT book_id, 'config_final', 'running' FROM candidate
    ON CONFLICT DO NOTHING
    RETURNING raport_id, book_id
)
SELECT c.raport_id, c.book_id, b.title, b.pdf
FROM claimed c JOIN books b USING (book_id);
