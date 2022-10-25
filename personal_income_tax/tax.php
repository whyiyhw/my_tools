<?php

$income = 23000;    // 收入

$sumRealIncome = 0; // 真实收入

$gjzTaxRate = 0.12; // 公积金税率

$sumGjz = 0;        // 缴纳公积金总数

$sumIncome = 0;     // 总收入

$startingPoint = 5000;

$sumTax = 0;

$month = 0;

$calc = function (string $forceTaxIncome): string {

    if ($forceTaxIncome < 36000) {
        echo "小于 36000,税率 3%" . PHP_EOL;
        return bcmul($forceTaxIncome, 0.03, 2);
    }

    if ($forceTaxIncome < 144000) {
        echo "小于 144000,税率 10%" . PHP_EOL;
        return bcsub(bcmul($forceTaxIncome, 0.1, 2), 2520);
    }

    if ($forceTaxIncome < 300000) {
        echo "小于 300000,税率 20%" . PHP_EOL;
        return bcsub(bcmul($forceTaxIncome, 0.2, 2), 16920, 2);
    }

    if ($forceTaxIncome < 420000) {
        echo "小于 420000,税率 25%" . PHP_EOL;
        return bcsub(bcmul($forceTaxIncome, 0.25, 2), 31920, 2);
    }

    if ($forceTaxIncome < 660000) {
        echo "小于 660000,税率 30%" . PHP_EOL;
        return bcsub(bcmul($forceTaxIncome, 0.3, 2), 52920, 2);
    }

    if ($forceTaxIncome < 960000) {
        echo "小于 960000,税率 35%" . PHP_EOL;
        return bcsub(bcmul($forceTaxIncome, 0.35, 2), 85920, 2);
    }

    echo "大于 960000,税率 45%" . PHP_EOL;
    return bcsub(bcmul($forceTaxIncome, 0.45, 2), 181920, 2);
};

while ($month < 12) {
    $month++;
    echo "$month 月,收入 $income 元" . PHP_EOL;
    $sumIncome = bcadd($sumIncome, $income, 2);

    if ($income < $startingPoint) {
        continue;
    }

    $sumGjz = bcadd($sumGjz, bcmul(bcmul($income, $gjzTaxRate, 2), 2, 2), 2);

    // 单月保险
    $insurance =  bcadd(bcadd(bcadd(bcmul($income, 0.08, 2),  bcmul($income, 0.02, 2), 2), bcmul($income, 0.005, 2), 2), bcmul($income, $gjzTaxRate, 2), 2);

    $sumStartingPoint = bcmul($startingPoint, $month, 2);

    $sumInsurance = bcmul($insurance, $month, 2);

    echo "累计收入 $sumIncome 元,累计起征点免税 $sumStartingPoint 元, 累计保险 $sumInsurance 元" . PHP_EOL;
    $forceTaxIncome =  bcsub(bcsub($sumIncome, $sumStartingPoint, 2), $sumInsurance, 2);
    echo "累计需纳税金额 $forceTaxIncome 元" . PHP_EOL;

    $forceTax = $calc((string)$forceTaxIncome);

    $currTax = bcsub($forceTax, $sumTax, 2);

    $realIncome =  bcsub(bcsub($income, $insurance, 2), $currTax, 2);
    $sumRealIncome = bcadd($realIncome, $sumRealIncome, 2);
    echo "应纳税 $forceTax 元 ，已纳税 $sumTax 元，本月缴税 $currTax " . PHP_EOL;
    echo "本月到手 $realIncome 元，累计到手 $sumRealIncome 元 ，累计公积金 $sumGjz 元" . PHP_EOL . PHP_EOL;

    $sumTax = $forceTax;
}

echo "纳税总额可减免 " . (1500 * 12) . "元; " . PHP_EOL;
echo "实际应纳税总额 " . ($forceTaxIncome - 1500 * 12) . "元; " . PHP_EOL;
$realSumTax = $calc((string)($forceTaxIncome - 1500 * 12));
echo "目前总纳税 $forceTax 元，实际应纳税 $realSumTax 元; " . PHP_EOL;
$retreatTax = bcsub($forceTax, $realSumTax, 2);
echo "可退税 $retreatTax 元 " . PHP_EOL;
