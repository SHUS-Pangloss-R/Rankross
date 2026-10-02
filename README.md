# Rankross
This is my personal repository created to record my progress in machine learning
#2026.10.2
泰坦尼克生存率预测
使用Python&&Scikit-learn完成。
##方法
1；数据清洗：填补缺失值（此处我选择用均值），将性别转化成数字
2；特征工程：构造了（family_size，who(即为人特征：孩童，性别等)）以求得更优解
3；模型：随机森林（10树，5深）
4：结论：森林表现更优秀，0.82
####文件说明：题目中含有tatanic的ipynb文件中包含完整数据处理与模型训练代码
