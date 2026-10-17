#include <iomanip>//这个，是用于格式化输出
#include <iostream>

#include "unitlib.h"   



namespace {

struct Conversion {
    const char* title;       // 菜单上显示的名字
    const char* unitA;       // 第一组单位符号
    const char* unitB;       // 第二组单位符号
    double (*toB)(double);   // A -> B
    double (*toA)(double);   // B -> A
};

const Conversion kItems[] = {
    {"摄氏度 <-> 华氏度", "C",  "F",  Celsius_to_Fahrenheit, Fahrenheit_to_Celsius},
    {"米     <-> 英尺",   "m",  "ft", meter_to_foot,        foot_to_meter},
    {"千克   <-> 磅",     "kg", "lb", kilogram_to_pound,    pound_to_kilogram},
};

constexpr int kCount = static_cast<int>(sizeof(kItems) / sizeof(kItems[0]));

void printMenu() {
    std::cout << "\n============== 单位转换器 ==============\n";
    for (int i = 0; i < kCount; ++i) {
        std::cout << "  " << (i + 1) << ". " << kItems[i].title << "\n";
    }
    std::cout << "  0. 退出\n";
    std::cout << "========================================\n";
}

// 读一个 double；失败时清掉输入流的错误状态，返回 false
bool readDouble(double& out) {
    if (std::cin >> out) {
        return true;
    }
    std::cin.clear();
    std::cin.ignore(1024, '\n');
    return false;
}

}  // namespace

int main() {
    std::cout << std::fixed << std::setprecision(4);   // 结果统一保留 4 位小数

    while (true) {
        printMenu();
        std::cout << "请选择转换类型 (0-" << kCount << "): ";

        int choice = 0;
        if (!(std::cin >> choice)) {        // 输入不是数字（例如字母）时结束程序
            std::cout << "输入无效，程序结束。\n";
            break;
        }
        if (choice == 0) {
            break;
        }
        if (choice < 1 || choice > kCount) {
            std::cout << "无效的选择，请输入 0-" << kCount << "。\n";
            continue;
        }

        const Conversion& item = kItems[choice - 1];

        std::cout << "方向: 1) " << item.unitA << " -> " << item.unitB
                  << "   2) " << item.unitB << " -> " << item.unitA << " : ";

        int dir = 0;
        if (!(std::cin >> dir) || (dir != 1 && dir != 2)) {
            std::cout << "方向无效，请重新选择。\n";
            std::cin.clear();
            std::cin.ignore(1024, '\n');
            continue;
        }

        std::cout << "请输入数值: ";
        double value = 0.0;
        if (!readDouble(value)) {
            std::cout << "数值无效，请重新选择。\n";
            continue;
        }

        const double result = (dir == 1) ? item.toB(value) : item.toA(value);
        const char* from = (dir == 1) ? item.unitA : item.unitB;
        const char* to   = (dir == 1) ? item.unitB : item.unitA;

        std::cout << "结果: " << value << " " << from
                  << " = " << result << " " << to << "\n";
    }

    std::cout << "已退出，感谢使用。\n";
    return 0;
}
