//在这里，实现六个函数的实际功能

double Celsius_to_Fahrenheit (double C){
    return C * 9 / 5 + 32;
}

double Fahrenheit_to_Celsius ( double F){
    return (F - 32) * 5 / 9;
}

double meter_to_foot(double m){
    // 1 米 = 3.280839895 英尺 -> 米换英尺要"乘"
    return m * 3.280839895;
}

double foot_to_meter(double f){
    // 英尺换米要"除"，与上面互为逆运算
    return f / 3.280839895;
}

double pound_to_kilogram(double p){
    return p / 2.204622622;
}

double kilogram_to_pound(double kg){
    return kg * 2.204622622;
}