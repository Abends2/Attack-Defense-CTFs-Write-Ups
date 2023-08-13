#define CROW_MAIN
#include "crow.h"
#include "database.cpp"
#include "util_functions.cpp"
using namespace std;

[[noreturn]] void logrotate(){
    while(true) {
        system("/bin/bash -c 'if [[ $(find /var/log/skychat.txt -type f -size +100k 2>/dev/null) ]]; then cp /var/log/skychat.txt /var/log/skychat_old.txt; : > /var/log/skychat.txt; fi'");
        sleep(60 * 3);
    }
}

int main(){
    crow::SimpleApp app;
    if (!db_initialize()){
        CROW_LOG_WARNING << "Database connection error";
        return 1;
    }

    CROW_ROUTE(app, "/")([]{
        return crow::mustache::load("login.html").render();
    });

    CROW_ROUTE(app, "/register")([]{
        return crow::mustache::load("register.html").render();
    });

    CROW_ROUTE(app, "/chat")([]{
        return crow::mustache::load("chat.html").render();
    });

    CROW_ROUTE(app, "/api/v1/register")
    .methods("POST"_method)
    ([](const crow::request& req){
        auto x = crow::json::load(req.body);
        crow::json::wvalue json_res;
        if (!x){
            json_res["status"] = "Json error";
            return crow::response(400, json_res);
        }
        auto login = x["login"].s(), password = x["password"].s();
        User user = db_get_user(login);
        if (user.id >= 0){
            json_res["status"] = "Users exists";
            json_res["id"] = user.id;
            return crow::response(409, json_res);
        }
        int user_id = db_create_user(login, password);
        json_res["status"] = "ok";
        json_res["id"] = user_id;
        CROW_LOG_WARNING << "Registered user " << login << " with password " << password;
        return crow::response(201, json_res);
    });

    CROW_ROUTE(app, "/api/v1/login")
    .methods("POST"_method)
    ([](const crow::request& req){
        auto x = crow::json::load(req.body);
        crow::json::wvalue json_res;
        if (!x){
            json_res["status"] = "Json error";
            return crow::response(400, json_res);
        }
        auto login = x["login"].s(), password = x["password"].s();
        User user = db_get_user(login);
        if (user.id == -1 || user.password != password){
            json_res["status"] = "Wrong login or password";
            return crow::response(403, json_res);
        }
        json_res["status"] = "ok";
        json_res["id"] = user.id;
        CROW_LOG_WARNING << "Login from user " << login;
        return crow::response(200, json_res);
    });

    CROW_ROUTE(app, "/api/v1/chats")
    .methods("GET"_method, "POST"_method)
    ([](const crow::request& req){
        crow::json::wvalue json_res;
        User cur_user = authorize(get_header_value(req.headers, "Authorization"));
        if (cur_user.id < 0){
            json_res["status"] = "Authorization error";
            return crow::response(403, json_res);
        }
        if (req.method == "GET"_method){
            vector<Chat> found = db_get_chats(cur_user.id);
            for (int i = 0; i < found.size(); i++)
                json_res["data"][i] = found[i].toJson();
        }
        else{ // POST
            db_create_chat(cur_user.id);
            CROW_LOG_WARNING << "Chat created for user " << cur_user.login;
        }
        json_res["status"] = "ok";
        return crow::response(200, json_res);
    });

    CROW_ROUTE(app, "/api/v1/chats/<int>")
    .methods("GET"_method, "POST"_method)
    ([](const crow::request& req, int chat_id){
        crow::json::wvalue json_res;
        User cur_user = authorize(get_header_value(req.headers, "Authorization"));
        if (req.method == "GET"_method){
            Chat chat = db_get_chat(chat_id);
            if (!cur_user.is_admin && chat.user_id != cur_user.id && !chat.is_deleted){
                json_res["status"] = "Forbidden";
                json_res["id"] = chat.user_id;
                return crow::response(403, json_res);
            }
            vector<Message> found = db_get_messages(chat_id);
            for (int i = 0; i < found.size(); i++)
                json_res["data"][i] = found[i].toJson();
        }
        else if (req.method == "POST"_method){
            auto x = crow::json::load(req.body);
            Chat chat = db_get_chat(chat_id);
            if (chat.user_id != cur_user.id){
                json_res["status"] = "Forbidden";
                return crow::response(400, json_res);
            }
            db_create_message(chat_id, x["text"].s(), x["direction"].b());
            CROW_LOG_WARNING << "Message posted by user " << cur_user.login << " with length " << x["text"].size();
        }
        json_res["status"] = "ok";
        return crow::response(200, json_res);
    });

    CROW_ROUTE(app, "/api/v1/delete_chat")
    .methods("POST"_method)
    ([](const crow::request& req){
        auto x = crow::json::load(req.body);
        crow::json::wvalue json_res;
        if (!x){
            json_res["status"] = "Json error";
            return crow::response(400, json_res);
        }
        User user = authorize(get_header_value(req.headers, "Authorization"));
        if (user.id < 0){
            json_res["status"] = "Authorization error";
            return crow::response(403, json_res);
        }
        int chat_id = (int)x["chat_id"].i(), user_id = (int)x["user_id"].i();
        Chat chat = db_get_chat(chat_id);
        if (chat.user_id != user_id){
            json_res["status"] = "Authorization error";
            return crow::response(403, json_res);
        }
        db_delete_chat(chat_id, user.id);
        json_res["status"] = "ok";
        CROW_LOG_WARNING << "Chat " << chat_id << " deleted";
        return crow::response(200, json_res);
    });

    CROW_ROUTE(app, "/api/v1/update_msg")
    .methods("POST"_method)
    ([](const crow::request& req){
        auto x = crow::json::load(req.body);
        crow::json::wvalue json_res;
        if (!x){
            json_res["status"] = "Json error";
            return crow::response(400, json_res);
        }
        User user = authorize(get_header_value(req.headers, "Authorization"));
        if (user.id < 0){
            json_res["status"] = "Authorization error";
            return crow::response(403, json_res);
        }
        int msg_id = (int)x["msg_id"].i();
        string text = x["text"].s();
        if (db_get_chat(db_get_message(msg_id).chat_id).user_id != user.id){
            json_res["status"] = "Authorization error";
            return crow::response(403, json_res);
        }
        db_update_message(msg_id, text);
        json_res["status"] = "ok";
        CROW_LOG_WARNING << "Message " << msg_id << " updated";
        return crow::response(200, json_res);
    });

    thread logrotate_thread(logrotate);
    app.loglevel(crow::LogLevel::Warning);
    CROW_LOG_WARNING << "Starting server";
    app.port(18080).multithreaded().run();
}