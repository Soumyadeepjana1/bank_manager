#include <iostream>
#include <string>
#include "sqlite3.h"

// Define the database path
const char* DB_FILE = "bank.db";

// Helper function to execute SQL
int execute_sql(sqlite3* db, const char* sql, char** err_msg) {
    return sqlite3_exec(db, sql, 0, 0, err_msg);
}

extern "C" {

// Initialize the database and create table if it doesn't exist
int init_db() {
    sqlite3* db;
    int rc = sqlite3_open(DB_FILE, &db);
    if (rc) {
        std::cerr << "Can't open database: " << sqlite3_errmsg(db) << std::endl;
        return 0;
    }

    const char* sql = "CREATE TABLE IF NOT EXISTS accounts("
                      "id INTEGER PRIMARY KEY AUTOINCREMENT,"
                      "name TEXT NOT NULL,"
                      "balance REAL NOT NULL);";
                      
    char* err_msg = nullptr;
    rc = execute_sql(db, sql, &err_msg);
    
    if (rc != SQLITE_OK) {
        std::cerr << "SQL error: " << err_msg << std::endl;
        sqlite3_free(err_msg);
        sqlite3_close(db);
        return 0;
    }
    
    sqlite3_close(db);
    return 1;
}

// Create an account and return its ID
int create_account(const char* name, double initial_balance) {
    sqlite3* db;
    int rc = sqlite3_open(DB_FILE, &db);
    if (rc) return -1;

    std::string sql = "INSERT INTO accounts (name, balance) VALUES ('" + std::string(name) + "', " + std::to_string(initial_balance) + ");";
    
    char* err_msg = nullptr;
    rc = execute_sql(db, sql.c_str(), &err_msg);
    
    if (rc != SQLITE_OK) {
        sqlite3_free(err_msg);
        sqlite3_close(db);
        return -1;
    }
    
    int id = sqlite3_last_insert_rowid(db);
    sqlite3_close(db);
    return id;
}

// Get account balance
double get_balance(int account_id) {
    sqlite3* db;
    int rc = sqlite3_open(DB_FILE, &db);
    if (rc) return -1.0;

    std::string sql = "SELECT balance FROM accounts WHERE id = " + std::to_string(account_id) + ";";
    sqlite3_stmt* stmt;
    rc = sqlite3_prepare_v2(db, sql.c_str(), -1, &stmt, NULL);
    
    double balance = -1.0;
    if (rc == SQLITE_OK) {
        if (sqlite3_step(stmt) == SQLITE_ROW) {
            balance = sqlite3_column_double(stmt, 0);
        }
    }
    
    sqlite3_finalize(stmt);
    sqlite3_close(db);
    return balance;
}

// Deposit amount into account
int deposit(int account_id, double amount) {
    if (amount <= 0) return 0;
    
    sqlite3* db;
    int rc = sqlite3_open(DB_FILE, &db);
    if (rc) return 0;

    std::string sql = "UPDATE accounts SET balance = balance + " + std::to_string(amount) + " WHERE id = " + std::to_string(account_id) + ";";
    char* err_msg = nullptr;
    rc = execute_sql(db, sql.c_str(), &err_msg);
    
    if (rc != SQLITE_OK) {
        sqlite3_free(err_msg);
        sqlite3_close(db);
        return 0;
    }
    
    // Check if any rows were affected
    int rows = sqlite3_changes(db);
    sqlite3_close(db);
    return rows > 0 ? 1 : 0;
}

// Withdraw amount from account
int withdraw(int account_id, double amount) {
    if (amount <= 0) return 0;
    
    sqlite3* db;
    int rc = sqlite3_open(DB_FILE, &db);
    if (rc) return 0;

    // Check balance first
    double balance = get_balance(account_id);
    if (balance < amount || balance == -1.0) {
        sqlite3_close(db);
        return 0;
    }

    std::string sql = "UPDATE accounts SET balance = balance - " + std::to_string(amount) + " WHERE id = " + std::to_string(account_id) + ";";
    char* err_msg = nullptr;
    rc = execute_sql(db, sql.c_str(), &err_msg);
    
    if (rc != SQLITE_OK) {
        sqlite3_free(err_msg);
        sqlite3_close(db);
        return 0;
    }

    int rows = sqlite3_changes(db);
    sqlite3_close(db);
    return rows > 0 ? 1 : 0;
}

} // extern "C"
