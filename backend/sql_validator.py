import sqlparse


def is_safe_sql(query: str) -> tuple[bool, str]:
    """
    Validates a SQL query to ensure it is read-only and safe to execute.
    Returns (is_safe, reason).
    """
    # 1. Parse and validate statements
    statements = sqlparse.parse(query)
    if not statements:
        return False, "Empty query."

    # 2. Extract actual statements, ignoring pure comments/whitespace
    valid_statements = [s for s in statements if s.get_type() != "UNKNOWN"]
    
    if len(valid_statements) > 1:
        return False, "Multiple statements are not allowed."

    stmt = valid_statements[0]
    
    # 3. Check statement type whitelist
    stmt_type = stmt.get_type().upper()
    if stmt_type != "SELECT":
        return False, f"Only SELECT queries are allowed. Found: {stmt_type}"

    # 4. Check for dangerous keywords inside the statement
    dangerous_keywords = {
        "INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "CREATE", 
        "TRUNCATE", "GRANT", "REVOKE", "EXECUTE", "COPY", "COMMIT"
    }

    # Iterate through all tokens recursively
    def check_tokens(token_list):
        for token in token_list:
            if token.is_group:
                check_tokens(token.tokens)
            else:
                if str(token.normalized).upper() in dangerous_keywords:
                    return str(token.normalized).upper()
        return None

    bad_keyword = check_tokens(stmt.tokens)
    if bad_keyword:
        return False, f"Forbidden keyword found in query: {bad_keyword}"

    return True, "Safe"
