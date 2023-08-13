#include <string>
#include "database.cpp"
using namespace std;

inline static std::string base64decode(const char* data, size_t size)
{
    // We accept both regular and url encoding here, as there does not seem to be any downside to that.
    // If we want to distinguish that we should use +/ for non-url and -_ for url.

    // Mapping logic from characters to [0-63]
    auto key = [](char c) -> unsigned char {
        if ((c >= 'A') && (c <= 'Z')) return c - 'A';
        if ((c >= 'a') && (c <= 'z')) return c - 'a' + 26;
        if ((c >= '0') && (c <= '9')) return c - '0' + 52;
        if ((c == '+') || (c == '-')) return 62;
        if ((c == '/') || (c == '_')) return 63;
        return 0;
    };

    // Not padded
    if (size % 4 == 2)             // missing last 2 characters
        size = (size / 4 * 3) + 1; // Not subtracting extra characters because they're truncated in int division
    else if (size % 4 == 3)        // missing last character
        size = (size / 4 * 3) + 2; // Not subtracting extra characters because they're truncated in int division

        // Padded
    else if (data[size - 2] == '=') // padded with '=='
        size = (size / 4 * 3) - 2;  // == padding means the last block only has 1 character instead of 3, hence the '-2'
    else if (data[size - 1] == '=') // padded with '='
        size = (size / 4 * 3) - 1;  // = padding means the last block only has 2 character instead of 3, hence the '-1'

        // Padding not needed
    else
        size = size / 4 * 3;

    std::string ret;
    ret.resize(size);
    auto it = ret.begin();

    // These will be used to decode 1 character at a time
    unsigned char odd;  // char1 and char3
    unsigned char even; // char2 and char4

    // Take 4 character blocks to turn into 3
    while (size >= 3)
    {
        // dec_char1 = (char1 shifted 2 bits to the left) OR ((char2 AND 00110000) shifted 4 bits to the right)
        odd = key(*data++);
        even = key(*data++);
        *it++ = (odd << 2) | ((even & 0x30) >> 4);
        // dec_char2 = ((char2 AND 00001111) shifted 4 bits left) OR ((char3 AND 00111100) shifted 2 bits right)
        odd = key(*data++);
        *it++ = ((even & 0x0F) << 4) | ((odd & 0x3C) >> 2);
        // dec_char3 = ((char3 AND 00000011) shifted 6 bits left) OR (char4)
        even = key(*data++);
        *it++ = ((odd & 0x03) << 6) | (even);

        size -= 3;
    }
    if (size == 2)
    {
        // d_char1 = (char1 shifted 2 bits to the left) OR ((char2 AND 00110000) shifted 4 bits to the right)
        odd = key(*data++);
        even = key(*data++);
        *it++ = (odd << 2) | ((even & 0x30) >> 4);
        // d_char2 = ((char2 AND 00001111) shifted 4 bits left) OR ((char3 AND 00111100) shifted 2 bits right)
        odd = key(*data++);
        *it++ = ((even & 0x0F) << 4) | ((odd & 0x3C) >> 2);
    }
    else if (size == 1)
    {
        // d_char1 = (char1 shifted 2 bits to the left) OR ((char2 AND 00110000) shifted 4 bits to the right)
        odd = key(*data++);
        even = key(*data++);
        *it++ = (odd << 2) | ((even & 0x30) >> 4);
    }
    return ret;
}

inline static std::string base64decode(const std::string& data, size_t size)
{
    return base64decode(data.data(), size);
}

inline static std::string base64decode(const std::string& data)
{
    return base64decode(data.data(), data.length());
}


User authorize(const string& myauth){
    string mycreds = myauth.substr(6);
    string d_mycreds = base64decode(mycreds);
    size_t found = d_mycreds.find(':');
    string login = d_mycreds.substr(0, found);
    string password = d_mycreds.substr(found+1);
    User user = db_get_user(login);
    if (password == user.password)
        return user;
    else return {-1, "", "", true};
}