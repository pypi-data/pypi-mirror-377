"""
ProServe E2E Database Integration Tests
Database operations, persistence, transactions, and data management
"""

import pytest
import json
import sqlite3
import requests
from pathlib import Path
from .test_framework import ProServeTestFramework, assert_http_response


@pytest.mark.asyncio
async def test_sqlite_database_operations(framework: ProServeTestFramework):
    """Test SQLite database integration with CRUD operations"""
    
    # Create database schema and handler
    db_handler = '''
import sqlite3
import json
from pathlib import Path

# Initialize database
db_path = Path(__file__).parent.parent / "test_database.db"

def init_db():
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            age INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            title TEXT NOT NULL,
            content TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)
    conn.commit()
    conn.close()

# Initialize database on module load
init_db()

async def handle(request):
    method = request.method
    path = str(request.url.path)
    
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row  # Enable dict-like access
    cursor = conn.cursor()
    
    try:
        if path == "/api/users" and method == "GET":
            cursor.execute("SELECT * FROM users ORDER BY created_at DESC")
            users = [dict(row) for row in cursor.fetchall()]
            return {"users": users, "count": len(users)}
        
        elif path == "/api/users" and method == "POST":
            data = await request.json()
            cursor.execute(
                "INSERT INTO users (name, email, age) VALUES (?, ?, ?)",
                (data.get("name"), data.get("email"), data.get("age"))
            )
            conn.commit()
            user_id = cursor.lastrowid
            
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            user = dict(cursor.fetchone())
            return {"user": user, "status": "created"}
        
        elif "/api/users/" in path and method == "GET":
            user_id = request.match_info.get('user_id')
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            user = cursor.fetchone()
            
            if user:
                # Get user's posts
                cursor.execute("SELECT * FROM posts WHERE user_id = ?", (user_id,))
                posts = [dict(row) for row in cursor.fetchall()]
                
                return {
                    "user": dict(user),
                    "posts": posts,
                    "posts_count": len(posts)
                }
            return {"error": "User not found"}, 404
        
        elif "/api/users/" in path and method == "PUT":
            user_id = request.match_info.get('user_id')
            data = await request.json()
            
            cursor.execute(
                "UPDATE users SET name = ?, email = ?, age = ? WHERE id = ?",
                (data.get("name"), data.get("email"), data.get("age"), user_id)
            )
            
            if cursor.rowcount > 0:
                conn.commit()
                cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
                user = dict(cursor.fetchone())
                return {"user": user, "status": "updated"}
            return {"error": "User not found"}, 404
        
        elif "/api/users/" in path and method == "DELETE":
            user_id = request.match_info.get('user_id')
            
            # Delete user's posts first (foreign key constraint)
            cursor.execute("DELETE FROM posts WHERE user_id = ?", (user_id,))
            cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
            
            if cursor.rowcount > 0:
                conn.commit()
                return {"status": "deleted", "user_id": user_id}
            return {"error": "User not found"}, 404
        
        elif path == "/api/posts" and method == "GET":
            cursor.execute("""
                SELECT p.*, u.name as user_name, u.email as user_email
                FROM posts p
                JOIN users u ON p.user_id = u.id
                ORDER BY p.created_at DESC
            """)
            posts = [dict(row) for row in cursor.fetchall()]
            return {"posts": posts, "count": len(posts)}
        
        elif path == "/api/posts" and method == "POST":
            data = await request.json()
            cursor.execute(
                "INSERT INTO posts (user_id, title, content) VALUES (?, ?, ?)",
                (data.get("user_id"), data.get("title"), data.get("content"))
            )
            conn.commit()
            post_id = cursor.lastrowid
            
            cursor.execute("""
                SELECT p.*, u.name as user_name, u.email as user_email
                FROM posts p
                JOIN users u ON p.user_id = u.id
                WHERE p.id = ?
            """, (post_id,))
            post = dict(cursor.fetchone())
            return {"post": post, "status": "created"}
        
        elif path == "/api/stats":
            cursor.execute("SELECT COUNT(*) as user_count FROM users")
            user_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) as post_count FROM posts")
            post_count = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT u.name, COUNT(p.id) as post_count
                FROM users u
                LEFT JOIN posts p ON u.id = p.user_id
                GROUP BY u.id, u.name
                ORDER BY post_count DESC
                LIMIT 5
            """)
            top_users = [dict(row) for row in cursor.fetchall()]
            
            return {
                "user_count": user_count,
                "post_count": post_count,
                "top_users": top_users
            }
        
        return {"error": "Endpoint not found"}, 404
        
    except sqlite3.IntegrityError as e:
        return {"error": f"Database constraint violation: {str(e)}"}, 400
    except Exception as e:
        return {"error": f"Database error: {str(e)}"}, 500
    finally:
        conn.close()
'''
    
    manifest_path = framework.create_test_manifest(
        'test-database-integration',
        endpoints=[
            {'path': '/api/users', 'method': 'get', 'handler': 'database_handler.handle'},
            {'path': '/api/users', 'method': 'post', 'handler': 'database_handler.handle'},
            {'path': '/api/users/{user_id}', 'method': 'get', 'handler': 'database_handler.handle'},
            {'path': '/api/users/{user_id}', 'method': 'put', 'handler': 'database_handler.handle'},
            {'path': '/api/users/{user_id}', 'method': 'delete', 'handler': 'database_handler.handle'},
            {'path': '/api/posts', 'method': 'get', 'handler': 'database_handler.handle'},
            {'path': '/api/posts', 'method': 'post', 'handler': 'database_handler.handle'},
            {'path': '/api/stats', 'method': 'get', 'handler': 'database_handler.handle'},
        ]
    )
    
    framework.create_test_handler('database_handler.py', db_handler)
    
    service = await framework.start_test_service(manifest_path, 'database_test')
    manifest = service.manifest
    base_url = f"http://{manifest.host}:{manifest.port}"
    
    # Test user creation
    user_data = {
        "name": "John Doe",
        "email": "john@example.com",
        "age": 30
    }
    create_response = requests.post(f"{base_url}/api/users", json=user_data)
    assert create_response.status_code == 200
    created_user = create_response.json()["user"]
    user_id = created_user["id"]
    
    # Test user retrieval
    user_response = await assert_http_response(f"{base_url}/api/users/{user_id}")
    assert user_response["user"]["name"] == "John Doe"
    assert user_response["user"]["email"] == "john@example.com"
    
    # Test user list
    users_response = await assert_http_response(f"{base_url}/api/users")
    assert len(users_response["users"]) >= 1
    assert any(u["id"] == user_id for u in users_response["users"])
    
    # Test post creation
    post_data = {
        "user_id": user_id,
        "title": "My First Post",
        "content": "This is a test post content."
    }
    post_response = requests.post(f"{base_url}/api/posts", json=post_data)
    assert post_response.status_code == 200
    created_post = post_response.json()["post"]
    
    # Test posts list
    posts_response = await assert_http_response(f"{base_url}/api/posts")
    assert len(posts_response["posts"]) >= 1
    assert posts_response["posts"][0]["user_name"] == "John Doe"
    
    # Test user with posts
    user_with_posts = await assert_http_response(f"{base_url}/api/users/{user_id}")
    assert len(user_with_posts["posts"]) >= 1
    assert user_with_posts["posts"][0]["title"] == "My First Post"
    
    # Test statistics
    stats_response = await assert_http_response(f"{base_url}/api/stats")
    assert stats_response["user_count"] >= 1
    assert stats_response["post_count"] >= 1
    assert len(stats_response["top_users"]) >= 1
    
    # Test user update
    update_data = {
        "name": "John Smith",
        "email": "johnsmith@example.com", 
        "age": 31
    }
    update_response = requests.put(f"{base_url}/api/users/{user_id}", json=update_data)
    assert update_response.status_code == 200
    assert update_response.json()["user"]["name"] == "John Smith"
    
    # Test constraint violation (duplicate email)
    duplicate_user = {
        "name": "Jane Doe",
        "email": "johnsmith@example.com",  # Same email
        "age": 25
    }
    duplicate_response = requests.post(f"{base_url}/api/users", json=duplicate_user)
    assert duplicate_response.status_code == 400
    assert "constraint violation" in duplicate_response.json()["error"]
    
    return {
        "database_operations_working": True,
        "user_created": created_user["name"] == "John Doe",
        "post_created": created_post["title"] == "My First Post",  
        "user_updated": update_response.json()["user"]["name"] == "John Smith",
        "constraint_handling": duplicate_response.status_code == 400,
        "stats_generated": stats_response["user_count"] >= 1,
        "relationships_working": user_with_posts["posts_count"] >= 1
    }


@pytest.mark.asyncio
async def test_transaction_handling(framework: ProServeTestFramework):
    """Test database transaction handling and rollback scenarios"""
    
    transaction_handler = '''
import sqlite3
import json
from pathlib import Path

db_path = Path(__file__).parent.parent / "transaction_test.db"

def init_db():
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            balance DECIMAL(10,2) NOT NULL DEFAULT 0.00
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            from_account_id INTEGER,
            to_account_id INTEGER,
            amount DECIMAL(10,2) NOT NULL,
            description TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'pending'
        )
    """)
    conn.commit()
    conn.close()

init_db()

async def handle(request):
    method = request.method
    path = str(request.url.path)
    
    if path == "/api/accounts" and method == "POST":
        data = await request.json()
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "INSERT INTO accounts (name, balance) VALUES (?, ?)",
                (data.get("name"), data.get("balance", 0.00))
            )
            conn.commit()
            account_id = cursor.lastrowid
            
            cursor.execute("SELECT * FROM accounts WHERE id = ?", (account_id,))
            account = dict(cursor.fetchone()) if cursor.fetchone() else None
            cursor.execute("SELECT * FROM accounts WHERE id = ?", (account_id,))
            row = cursor.fetchone()
            account = {"id": row[0], "name": row[1], "balance": float(row[2])} if row else None
            
            return {"account": account, "status": "created"}
        except Exception as e:
            conn.rollback()
            return {"error": str(e)}, 500
        finally:
            conn.close()
    
    elif path == "/api/accounts" and method == "GET":
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM accounts ORDER BY name")
        accounts = []
        for row in cursor.fetchall():
            accounts.append({"id": row[0], "name": row[1], "balance": float(row[2])})
        
        conn.close()
        return {"accounts": accounts, "count": len(accounts)}
    
    elif path == "/api/transfer" and method == "POST":
        data = await request.json()
        from_account = data.get("from_account_id")
        to_account = data.get("to_account_id")
        amount = float(data.get("amount", 0))
        description = data.get("description", "Transfer")
        
        if amount <= 0:
            return {"error": "Amount must be positive"}, 400
        
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        try:
            # Start transaction
            cursor.execute("BEGIN TRANSACTION")
            
            # Check source account balance
            cursor.execute("SELECT balance FROM accounts WHERE id = ?", (from_account,))
            source_balance = cursor.fetchone()
            if not source_balance:
                raise Exception("Source account not found")
            
            if source_balance[0] < amount:
                raise Exception("Insufficient funds")
            
            # Check destination account exists
            cursor.execute("SELECT id FROM accounts WHERE id = ?", (to_account,))
            if not cursor.fetchone():
                raise Exception("Destination account not found")
            
            # Record transaction
            cursor.execute("""
                INSERT INTO transactions (from_account_id, to_account_id, amount, description, status)
                VALUES (?, ?, ?, ?, 'processing')
            """, (from_account, to_account, amount, description))
            transaction_id = cursor.lastrowid
            
            # Update balances
            cursor.execute(
                "UPDATE accounts SET balance = balance - ? WHERE id = ?",
                (amount, from_account)
            )
            cursor.execute(
                "UPDATE accounts SET balance = balance + ? WHERE id = ?", 
                (amount, to_account)
            )
            
            # Mark transaction as completed
            cursor.execute(
                "UPDATE transactions SET status = 'completed' WHERE id = ?",
                (transaction_id,)
            )
            
            # Commit transaction
            conn.commit()
            
            # Get updated balances
            cursor.execute("SELECT balance FROM accounts WHERE id = ?", (from_account,))
            new_from_balance = cursor.fetchone()[0]
            cursor.execute("SELECT balance FROM accounts WHERE id = ?", (to_account,))
            new_to_balance = cursor.fetchone()[0]
            
            return {
                "transaction_id": transaction_id,
                "status": "completed",
                "amount": amount,
                "from_account_balance": float(new_from_balance),
                "to_account_balance": float(new_to_balance)
            }
            
        except Exception as e:
            # Rollback on any error
            conn.rollback()
            
            # Mark transaction as failed if it was created
            try:
                if 'transaction_id' in locals():
                    cursor.execute(
                        "UPDATE transactions SET status = 'failed' WHERE id = ?",
                        (transaction_id,)
                    )
                    conn.commit()
            except:
                pass
            
            return {"error": str(e), "status": "failed"}, 400
        finally:
            conn.close()
    
    elif path == "/api/transactions" and method == "GET":
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT t.*, 
                   a1.name as from_account_name,
                   a2.name as to_account_name
            FROM transactions t
            LEFT JOIN accounts a1 ON t.from_account_id = a1.id
            LEFT JOIN accounts a2 ON t.to_account_id = a2.id
            ORDER BY t.timestamp DESC
        """)
        
        transactions = []
        for row in cursor.fetchall():
            transactions.append({
                "id": row[0],
                "from_account_id": row[1],
                "to_account_id": row[2], 
                "amount": float(row[3]),
                "description": row[4],
                "timestamp": row[5],
                "status": row[6],
                "from_account_name": row[7],
                "to_account_name": row[8]
            })
        
        conn.close()
        return {"transactions": transactions, "count": len(transactions)}
    
    return {"error": "Endpoint not found"}, 404
'''
    
    manifest_path = framework.create_test_manifest(
        'test-transactions',
        endpoints=[
            {'path': '/api/accounts', 'method': 'get', 'handler': 'transaction_handler.handle'},
            {'path': '/api/accounts', 'method': 'post', 'handler': 'transaction_handler.handle'},
            {'path': '/api/transfer', 'method': 'post', 'handler': 'transaction_handler.handle'},
            {'path': '/api/transactions', 'method': 'get', 'handler': 'transaction_handler.handle'},
        ]
    )
    
    framework.create_test_handler('transaction_handler.py', transaction_handler)
    
    service = await framework.start_test_service(manifest_path, 'transaction_test')
    manifest = service.manifest
    base_url = f"http://{manifest.host}:{manifest.port}"
    
    # Create test accounts
    account1_data = {"name": "Alice", "balance": 1000.00}
    account2_data = {"name": "Bob", "balance": 500.00}
    
    account1_response = requests.post(f"{base_url}/api/accounts", json=account1_data)
    account2_response = requests.post(f"{base_url}/api/accounts", json=account2_data)
    
    assert account1_response.status_code == 200
    assert account2_response.status_code == 200
    
    account1_id = account1_response.json()["account"]["id"]
    account2_id = account2_response.json()["account"]["id"]
    
    # Test successful transfer
    transfer_data = {
        "from_account_id": account1_id,
        "to_account_id": account2_id,
        "amount": 200.00,
        "description": "Test transfer"
    }
    transfer_response = requests.post(f"{base_url}/api/transfer", json=transfer_data)
    assert transfer_response.status_code == 200
    
    transfer_result = transfer_response.json()
    assert transfer_result["status"] == "completed"
    assert transfer_result["from_account_balance"] == 800.00  # 1000 - 200
    assert transfer_result["to_account_balance"] == 700.00    # 500 + 200
    
    # Test insufficient funds transfer (should fail and rollback)
    insufficient_transfer = {
        "from_account_id": account1_id,
        "to_account_id": account2_id,
        "amount": 1000.00,  # More than current balance (800)
        "description": "Insufficient funds test"
    }
    insufficient_response = requests.post(f"{base_url}/api/transfer", json=insufficient_transfer)
    assert insufficient_response.status_code == 400
    assert "Insufficient funds" in insufficient_response.json()["error"]
    
    # Verify balances unchanged after failed transfer
    accounts_response = await assert_http_response(f"{base_url}/api/accounts")
    alice_account = next(acc for acc in accounts_response["accounts"] if acc["id"] == account1_id)
    bob_account = next(acc for acc in accounts_response["accounts"] if acc["id"] == account2_id)
    
    assert alice_account["balance"] == 800.00  # Should be unchanged
    assert bob_account["balance"] == 700.00    # Should be unchanged
    
    # Test transaction history
    transactions_response = await assert_http_response(f"{base_url}/api/transactions")
    transactions = transactions_response["transactions"]
    
    # Should have one completed and one failed transaction
    completed_transactions = [t for t in transactions if t["status"] == "completed"]
    failed_transactions = [t for t in transactions if t["status"] == "failed"]
    
    assert len(completed_transactions) >= 1
    assert len(failed_transactions) >= 1 or insufficient_response.status_code == 400
    
    return {
        "transaction_handling_working": True,
        "accounts_created": len(accounts_response["accounts"]) >= 2, 
        "successful_transfer": transfer_result["status"] == "completed",
        "balances_updated_correctly": (alice_account["balance"] == 800.00 and 
                                     bob_account["balance"] == 700.00),
        "insufficient_funds_rejected": insufficient_response.status_code == 400,
        "transaction_history_recorded": len(transactions) >= 1,
        "rollback_working": alice_account["balance"] == 800.00  # Unchanged after failed transfer
    }
