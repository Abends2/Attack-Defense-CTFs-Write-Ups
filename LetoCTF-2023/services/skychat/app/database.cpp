#ifndef DATABASE_CPP
#define DATABASE_CPP
#include <pqxx/pqxx>
#include "structs.h"
using namespace pqxx;

connection Conn("dbname = db user = admin password = admin host = db port = 5432");

bool db_initialize() {
    if (!Conn.is_open()) return false;
    string sql = "CREATE TABLE IF NOT EXISTS Users("  \
                  "id SERIAL PRIMARY KEY," \
                  "login TEXT DEFAULT ''," \
                  "password TEXT DEFAULT ''," \
                  "is_admin BOOLEAN DEFAULT FALSE);";
    string sql2 = "CREATE TABLE IF NOT EXISTS Chats("  \
                  "id SERIAL PRIMARY KEY," \
                  "user_id INTEGER," \
                  "is_deleted BOOL DEFAULT FALSE);";
    string sql3 = "CREATE TABLE IF NOT EXISTS Messages("  \
                  "id SERIAL PRIMARY KEY," \
                  "chat_id INTEGER," \
                  "text TEXT," \
                  "direction BOOL);";
    work W(Conn);
    W.exec(sql);
    W.exec(sql2);
    W.exec(sql3);
    W.commit();
    return true;
}

int db_create_user(const string &login, const string &password) {
    work W(Conn);
    params p;
    p.reserve(2);
    p.append(login);
    p.append(password);
    auto r = W.exec_params("INSERT INTO Users (login,password) VALUES ($1, $2) RETURNING id;", p);
    W.commit();
    if (!r.empty())
        return r.begin()[0].as<int>();
    return -1;
}

void db_create_chat(int user_id) {
    work W(Conn);
    params p;
    p.reserve(1);
    p.append(user_id);
    W.exec_params("INSERT INTO Chats (user_id) VALUES ($1)", p);
    W.commit();
}

void db_create_message(int chat_id, string text, bool direction) {
    work W(Conn);
    params p;
    p.reserve(3);
    p.append(chat_id);
    p.append(text);
    p.append(direction);
    W.exec_params("INSERT INTO Messages (chat_id, text, direction) VALUES ($1, $2, $3)", p);
    W.commit();
}

User db_get_user(const string &login) {
    work W(Conn);
    params p;
    p.reserve(1);
    p.append(login);
    auto r = W.exec_params("SELECT id, password, is_admin FROM Users WHERE login = $1", p);
    User res = User(-1, "", "", false);
    if (!r.empty()){
        int id = r.begin()[0].as<int>();
        auto password = r.begin()[1].as<string>();
        bool is_admin = r.begin()[2].as<bool>();
        res = User(id, login, password, is_admin);
    }
    return res;
}

Chat db_get_chat(const int &chat_id) {
    work W(Conn);
    params p;
    p.reserve(1);
    p.append(chat_id);
    auto r = W.exec_params("SELECT user_id, is_deleted FROM Chats WHERE id = $1", p);
    Chat res = Chat(-1, -1, true);
    if (!r.empty()){
        int user_id = r.begin()[0].as<int>();
        bool is_deleted = r.begin()[1].as<bool>();
        res = Chat(chat_id, user_id, is_deleted);
    }
    return res;
}

Message db_get_message(const int &msg_id) {
    work W(Conn);
    params p;
    p.reserve(1);
    p.append(msg_id);
    auto r = W.exec_params("SELECT chat_id, text, direction FROM Messages WHERE id = $1", p);
    Message res = Message(-1, -1, "", true);
    if (!r.empty()){
        int chat_id = r.begin()[0].as<int>();
        auto text = r.begin()[1].as<string>();
        bool direction = r.begin()[2].as<bool>();
        res = Message(msg_id, chat_id, text, direction);
    }
    return res;
}

vector<Chat> db_get_chats(const int &user_id) {
    work W(Conn);
    params p;
    p.reserve(1);
    p.append(user_id);
    auto r = W.exec_params("SELECT id, is_deleted FROM Chats WHERE user_id = $1 AND is_deleted = FALSE", p);
    vector<Chat> res;
    for (auto const &row: r){
        int id = row[0].as<int>();
        bool is_deleted = row[1].as<bool>();
        res.push_back(Chat(id, user_id, is_deleted));
    }
    return res;
}

vector<Message> db_get_messages(const int &chat_id) {
    work W(Conn);
    params p;
    p.reserve(1);
    p.append(chat_id);
    auto r = W.exec_params("SELECT id, text, direction FROM Messages WHERE chat_id = $1", p);
    vector<Message> res;
    for (auto const &row: r){
        int id = row[0].as<int>();
        auto text = row[1].as<string>();
        bool direction = row[2].as<bool>();
        res.push_back(Message(id, chat_id, text, direction));
    }
    return res;
}

void db_delete_chat(const int &chat_id, const int &user_id) {
    work W(Conn);
    params p;
    p.reserve(1);
    p.append(chat_id);
    W.exec_params("UPDATE Chats SET is_deleted = TRUE WHERE id = $1", p);
    W.commit();
}

void db_update_message(int message_id, string &text) {
    work W(Conn);
    params p;
    p.reserve(1);
    p.append(message_id);
    if (text.find(';') != std::string::npos) return;
    W.exec_params("UPDATE Messages SET text = '"+text+"' WHERE id = $1", p);
    W.commit();
}

#endif //DATABASE_CPP