#ifndef CODE_STRUCTS_H
#define CODE_STRUCTS_H
#include <string>
#include <utility>
#include "crow/json.h"
using namespace std;

struct User{
    int id;
    string login, password;
    bool is_admin;
    User(int _id, string _login, string _password, bool _is_admin){
        id = _id;
        login = std::move(_login);
        password = std::move(_password);
        is_admin = _is_admin;
    }
    [[nodiscard]] crow::json::wvalue toJson() const{
        crow::json::wvalue json_res;
        json_res["id"] = id;
        json_res["login"] = login;
        json_res["password"] = password;
        json_res["is_admin"] = is_admin;
        return json_res;
    }
};

struct Chat{
    int id;
    int user_id;
    bool is_deleted;
    Chat(int _id, int _user_id, bool _is_deleted){
        id = _id;
        user_id = _user_id;
        is_deleted = _is_deleted;
    }
    [[nodiscard]] crow::json::wvalue toJson() const{
        crow::json::wvalue json_res;
        json_res["id"] = id;
        json_res["user_id"] = user_id;
        json_res["is_deleted"] = is_deleted;
        return json_res;
    }
};

struct Message{
    int id;
    int chat_id;
    string text;
    bool direction;
    Message(int _id, int _chat_id, string _text, bool _direction){
        id = _id;
        chat_id = _chat_id;
        text = _text;
        direction = _direction;
    }
    [[nodiscard]] crow::json::wvalue toJson() const{
        crow::json::wvalue json_res;
        json_res["id"] = id;
        json_res["chat_id"] = chat_id;
        json_res["text"] = text;
        json_res["direction"] = direction;
        return json_res;
    }
};

#endif //CODE_STRUCTS_H
