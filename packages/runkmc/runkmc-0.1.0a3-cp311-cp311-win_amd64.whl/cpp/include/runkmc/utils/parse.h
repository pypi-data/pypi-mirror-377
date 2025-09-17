#pragma once
#include "utils/string.h"

#include <fstream>
#include <sstream>
#include <iterator>
#include "common.h"

namespace print
{
    static inline void printLine(std::string line)
    {
        std::cout << line << std::endl;
    }

    static inline void printLines(std::vector<std::string> lines)
    {
        for (auto line : lines)
            printLine(line);
    }

    template <typename T>
    static inline void printVector(std::vector<T> vec)
    {
        std::cout << "[";
        for (size_t i = 0; i < vec.size() - 1; ++i)
            std::cout << vec[i] << ", ";
        std::cout << vec[vec.size() - 1] << "]" << std::endl;
    }
};

namespace input
{
    static void trimLine(std::string &s) { str::trim(s); }

    static bool canIgnoreLine(std::string &line)
    {
        return line.size() == 0 ||
               str::startswith(line, "#") ||
               str::startswith(line, "/");
    }

    static std::vector<std::string> parseSection(std::string sectionName, std::ifstream &file)
    {
        std::string line;
        std::vector<std::string> section;
        bool sectionEnd = false;
        while (std::getline(file, line))
        {
            input::trimLine(line);
            if (canIgnoreLine(line))
                continue;
            if (str::startswith(line, "end"))
            {
                sectionEnd = true;
                break;
            };
            section.push_back(line);
        }

        if (sectionEnd)
            return section;
        else
        {
            std::cout << "Reached end of file while parsing " + sectionName + " section. ";
            std::cout << "Make sure to include \"end\" keyword at end of section." << std::endl;
            exit(EXIT_FAILURE);
        }
    }

    static std::vector<std::string> parseVariable(std::string s)
    {
        std::vector<std::string> splitstr = str::splitByDelimeter(s, "=");
        assert(splitstr.size() == 2);
        str::trim(splitstr[0]);
        str::trim(splitstr[1]);
        return splitstr;
    }

    template <typename T>
    static int getIndex(std::vector<T> v, T value)
    {
        auto it = std::find(v.begin(), v.end(), value);

        if (it != v.end())
        {
            int index = it - v.begin();
            return index;
        }
        else
            return -1;
    }

    template <typename T>
    size_t findInVector(std::string varName, std::vector<T> &vec)
    {
        for (size_t i = 0; i < vec.size(); ++i)
        {
            if (vec[i].name == varName)
            {
                return i;
            }
        }
        return vec.size();
    }

    /************************************************************************************************************/
    /************************************* Functions for reading variables **************************************/
    /************************************************************************************************************/

    /**
     * @brief Read a string variable.
     *
     * @param strings list of variable strings ("name"=value)
     * @param variableName name of variable to be read
     * @param variable reference to variable to be overwritten
     */
    static void readVariable(std::vector<std::string> strings, std::string variableName, std::string &variable)
    {
        bool found = false;
        for (auto &string : strings)
        {
            if (str::startswith(string, variableName))
            {
                std::vector<std::string> var = input::parseVariable(string);
                found = true;
                variable = var[1];
            }
        }
    }

    /**
     * @brief Read a double variable.
     *
     * @param strings list of variable strings ("name"=value)
     * @param variableName name of variable to be read
     * @param variable reference to variable to be overwritten
     */
    static void readVariable(std::vector<std::string> strings, std::string variableName, double &variable)
    {
        bool found = false;
        for (auto &string : strings)
        {
            if (str::startswith(string, variableName))
            {
                std::vector<std::string> var = input::parseVariable(string);
                found = true;
                variable = std::stod(var[1]);
            }
        }
    }

    /**
     * @brief Read a integer variable.
     *
     * @param strings list of variable strings ("name"=value)
     * @param variableName name of variable to be read
     * @param variable reference to variable to be overwritten
     */
    static void readVariable(std::vector<std::string> strings, std::string variableName, int &variable)
    {
        bool found = false;
        for (auto &string : strings)
        {
            if (str::startswith(string, variableName))
            {
                std::vector<std::string> var = input::parseVariable(string);
                found = true;
                variable = std::stoi(var[1]);
            }
        }
    }

    /**
     * @brief Read a required string variable.
     *
     * @param strings list of variable strings ("name"=value)
     * @param variableName name of variable to be read
     * @param variable reference to variable to be overwritten
     */
    static void readVariableRequired(std::vector<std::string> strings, std::string variableName, std::string &variable)
    {
        bool found = false;
        for (auto &string : strings)
        {
            if (str::startswith(string, variableName))
            {
                std::vector<std::string> var = input::parseVariable(string);
                found = true;
                variable = var[1];
            }
        }
        if (!found)
            console::input_error("Required variable " + variableName + " is not found.");
    }

    /**
     * @brief Read a required double variable.
     *
     * @param strings list of variable strings ("name"=value)
     * @param variableName name of variable to be read
     * @param variable reference to variable to be overwritten
     */
    static void readVariableRequired(std::vector<std::string> strings, std::string variableName, double &variable)
    {
        bool found = false;
        for (auto &string : strings)
        {
            if (str::startswith(string, variableName))
            {
                std::vector<std::string> var = input::parseVariable(string);
                found = true;
                variable = std::stod(var[1]);
                return;
            }
        }
        if (!found)
            console::input_error("Required variable " + variableName + " is not found.");
    }

    /**
     * @brief Read a required integer variable.
     *
     * @param strings list of variable strings ("name"=value)
     * @param variableName name of variable to be read
     * @param variable reference to variable to be overwritten
     */
    static void readVariableRequired(std::vector<std::string> strings, std::string variableName, uint64_t &variable)
    {
        bool found = false;
        for (auto &string : strings)
        {
            if (str::startswith(string, variableName))
            {
                std::vector<std::string> var = input::parseVariable(string);
                found = true;
                variable = static_cast<int64_t>(std::stod(var[1]));
            }
        }
        if (!found)
            console::input_error("Required variable " + variableName + " is not found.");
    }

};
