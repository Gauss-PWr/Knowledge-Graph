SELECT book_id, title,
       pg_size_pretty(octet_length(pdf)::bigint) AS pdf_size,
       md IS NOT NULL AS has_md
FROM books
ORDER BY book_id;

SELECT book_id, title from books