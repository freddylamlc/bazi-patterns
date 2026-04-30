/**
 * 八字排盤系統 - 前端 JavaScript
 * 主要功能：輸入模式切換、大運流年選擇、地支關係顯示、天干五合顯示
 */

// 地支沖刑關係對照表
const zhiRelations = {
    '子': ['午', '丑', '卯', '辰', '申', '亥'],
    '丑': ['未', '子', '巳', '酉', '寅', '辰'],
    '寅': ['申', '亥', '巳', '申', '巳', '丑'],
    '卯': ['酉', '戌', '子', '辰', '午', '辰'],
    '辰': ['戌', '申', '子', '卯', '寅', '丑'],
    '巳': ['亥', '寅', '申', '寅', '申', '寅'],
    '午': ['子', '未', '寅', '戌', '午', '午'],
    '未': ['丑', '午', '酉', '巳', '午', '午'],
    '申': ['寅', '巳', '辰', '亥', '寅', '寅'],
    '酉': ['卯', '辰', '巳', '戌', '未', '酉'],
    '戌': ['辰', '卯', '午', '酉', '酉', '戌'],
    '亥': ['巳', '寅', '卯', '申', '寅', '亥']
};

// 地支會合關係
const zhiHe = {
    '六合': [['子','丑'], ['丑','子'], ['寅','亥'], ['亥','寅'], ['卯','戌'], ['戌','卯'], ['辰','酉'], ['酉','辰'], ['巳','申'], ['申','巳'], ['午','未'], ['未','午']],
    '三合局': [['申','子','辰'], ['子','辰','申'], ['辰','申','子'], ['亥','卯','未'], ['卯','未','亥'], ['未','卯','亥'], ['寅','午','戌'], ['午','戌','寅'], ['戌','寅','午'], ['巳','酉','丑'], ['酉','丑','巳'], ['丑','酉','巳']],
    '三會方': [['寅','卯','辰'], ['卯','辰','寅'], ['辰','寅','卯'], ['巳','午','未'], ['午','未','巳'], ['未','午','巳'], ['申','酉','戌'], ['酉','戌','申'], ['戌','申','酉'], ['亥','子','丑'], ['子','丑','亥'], ['丑','亥','子']]
};

// 天干五合
const tianGanHe = {
    '甲': '己', '己': '甲',
    '乙': '庚', '庚': '乙',
    '丙': '辛', '辛': '丙',
    '丁': '壬', '壬': '丁',
    '戊': '癸', '癸': '戊'
};

// 五行顏色映射
const wuXingColors = {
    "木": { bg: "bg-green-50", text: "text-green-700", border: "border-green-200" },
    "火": { bg: "bg-red-50", text: "text-red-700", border: "border-red-200" },
    "土": { bg: "bg-yellow-50", text: "text-yellow-700", border: "border-yellow-200" },
    "金": { bg: "bg-gray-50", text: "text-gray-700", border: "border-gray-200" },
    "水": { bg: "bg-blue-50", text: "text-blue-700", border: "border-blue-200" }
};

// 天干五行
const ganWuXing = {
    "甲": "木", "乙": "木", "丙": "火", "丁": "火", "戊": "土", "己": "土", "庚": "金", "辛": "金", "壬": "水", "癸": "水"
};

// 地支五行
const zhiWuXing = {
    "子": "水", "丑": "土", "寅": "木", "卯": "木", "辰": "土", "巳": "火", "午": "火", "未": "土", "申": "金", "酉": "金", "戌": "土", "亥": "水"
};

// 全局變量
let currentDayunIndex = 0;
let currentLiunianIndex = 0;
let currentLiuyueIndex = 0;

// 初始化
document.addEventListener('DOMContentLoaded', function() {
    try {
        // [調試] 打印 JS 收到的數據
        console.log('\n[JS DEBUG] ===== JavaScript 初始化檢查 =====');
        console.log('[JS DEBUG] window.allLiunianData 長度:', (window.allLiunianData || []).length);
        console.log('[JS DEBUG] window.dayunData 長度:', (window.dayunData || []).length);
        console.log('[JS DEBUG] window.liunianByDayun 鍵:', Object.keys(window.liunianByDayun || {}));
        console.log('[JS DEBUG] window.fourPillars:', window.fourPillars);
        console.log('[JS DEBUG] 第一個大運:', (window.dayunData || [])?.[0]);
        console.log('[JS DEBUG] 第一個流年:', (window.allLiunianData || [])?.[0]);
        console.log('[JS DEBUG] liunianByDayun[0] 第一個:', (window.liunianByDayun && window.liunianByDayun[0]) ? window.liunianByDayun[0][0] : 'undefined');
        console.log('[JS DEBUG] window.suiyunGejuAll 長度:', (window.suiyunGejuAll || []).length);
        console.log('[JS DEBUG] window.suiyunGejuAll[0]:', (window.suiyunGejuAll && window.suiyunGejuAll[0]) ? window.suiyunGejuAll[0] : 'undefined');

        // 驗證數據
        if (!window.dayunData || window.dayunData.length === 0) {
            console.error('[JS 錯誤] window.dayunData 為空');
        }
        if (!window.allLiunianData || window.allLiunianData.length === 0) {
            console.error('[JS 錯誤] window.allLiunianData 為空');
        }
        if (!window.liunianByDayun || !window.liunianByDayun[0] || window.liunianByDayun[0].length === 0) {
            console.error('[JS 錯誤] window.liunianByDayun[0] 為空');
        }
        if (!window.suiyunGejuAll || window.suiyunGejuAll.length === 0) {
            console.error('[JS 錯誤] window.suiyunGejuAll 為空');
        }

        console.log('[JS DEBUG] 開始初始化流年柱...');
        updateLiunianPillars(0);
        console.log('[JS DEBUG] 開始初始化流月柱...');
        updateLiuyuePillars(0);
        console.log('[JS DEBUG] 開始更新地支關係...');
        updateZhiRelations();
        console.log('[JS DEBUG] 開始更新天干五合...');
        updateTianGanWuHe();
        console.log('[JS DEBUG] 開始初始化流年判斷區域...');
        updateLiunianJudgment(0);
        console.log('[JS DEBUG] 開始初始化歲運格局...');
        updateSuiyunGeju(0, 0);
        console.log('[JS DEBUG] ===========================\n');
    } catch (e) {
        console.error('[JS 初始化錯誤]', e);
    }
});

// 切換到日期輸入模式
function showDateInput() {
    document.getElementById('date-input-form').classList.remove('hidden');
    document.getElementById('pillar-input-form').classList.add('hidden');
    document.getElementById('btn-date-input').classList.remove('bg-stone-200', 'text-stone-700');
    document.getElementById('btn-date-input').classList.add('bg-stone-900', 'text-white');
    document.getElementById('btn-pillar-input').classList.remove('bg-stone-900', 'text-white');
    document.getElementById('btn-pillar-input').classList.add('bg-stone-200', 'text-stone-700');
}

// 切換到四柱輸入模式
function showPillarInput() {
    document.getElementById('date-input-form').classList.add('hidden');
    document.getElementById('pillar-input-form').classList.remove('hidden');
    document.getElementById('btn-pillar-input').classList.remove('bg-stone-200', 'text-stone-700');
    document.getElementById('btn-pillar-input').classList.add('bg-stone-900', 'text-white');
    document.getElementById('btn-date-input').classList.remove('bg-stone-900', 'text-white');
    document.getElementById('btn-date-input').classList.add('bg-stone-200', 'text-stone-700');
}

// 選擇大運
function selectDayun(index) {
    console.log('[selectDayun] 點擊大運索引:', index);
    currentDayunIndex = index;
    console.log('[selectDayun] currentDayunIndex 已設置為:', currentDayunIndex);

    // 更新大運選擇樣式
    document.querySelectorAll('.dayun-pillar-select').forEach((item, idx) => {
        if (idx === index) {
            item.classList.add('border-indigo-500', 'bg-indigo-50');
            item.classList.remove('border-stone-200', 'bg-stone-50');
        } else {
            item.classList.remove('border-indigo-500', 'bg-indigo-50');
            item.classList.add('border-stone-200', 'bg-stone-50');
        }
    });

    // 更新當前大運柱顯示
    if (window.dayunData[index]) {
        document.getElementById('current-dayun-gan').textContent = window.dayunData[index]['大運干'];
        document.getElementById('current-dayun-zhi').textContent = window.dayunData[index]['大運支'];
        document.getElementById('current-dayun-shishen').textContent = window.dayunData[index]['十神'];

        // 更新大運藏干
        const canggan = window.dayunData[index]['地支']['藏干'] || {};
        let cangganHtml = '';
        if (canggan['主氣'] && canggan['主氣']['干']) {
            const mainGan = canggan['主氣']['干'];
            const mainWX = ganWuXing[mainGan] || '土';
            const mainClass = wuXingColors[mainWX];
            cangganHtml += `<div class="flex justify-between text-[9px] w-full px-1 opacity-70"><span class="${mainClass.text}">${mainGan}</span><span class="text-stone-400">${canggan['主氣']['十神'] || ''}</span></div>`;
        }
        if (canggan['中氣'] && canggan['中氣']['干']) {
            const midGan = canggan['中氣']['干'];
            const midWX = ganWuXing[midGan] || '土';
            const midClass = wuXingColors[midWX];
            cangganHtml += `<div class="flex justify-between text-[9px] w-full px-1 opacity-70"><span class="${midClass.text}">${midGan}</span><span class="text-stone-400">${canggan['中氣']['十神'] || ''}</span></div>`;
        }
        if (canggan['餘氣'] && canggan['餘氣']['干']) {
            const restGan = canggan['餘氣']['干'];
            const restWX = ganWuXing[restGan] || '土';
            const restClass = wuXingColors[restWX];
            cangganHtml += `<div class="flex justify-between text-[9px] w-full px-1 opacity-70"><span class="${restClass.text}">${restGan}</span><span class="text-stone-400">${canggan['餘氣']['十神'] || ''}</span></div>`;
        }
        document.getElementById('current-dayun-canggan').innerHTML = cangganHtml;

        // 更新大運十二長生
        document.getElementById('current-dayun-changsheng').textContent = window.dayunData[index]['地支']['十二長生'] || '';
    }

    // 更新流年柱
    updateLiunianPillars(index);

    // 更新流月柱（重置為第一個流月）
    updateLiuyuePillars(index);

    // 更新大運與四柱沖刑關係
    updateZhiRelations();

    // 更新天干五合
    updateTianGanWuHe();

    // 更新流年判斷區域
    updateLiunianJudgment(index);

    // 更新歲運格局（重置為第一個流年）
    console.log('[selectDayun] 調用 updateSuiyunGeju(', index, ', 0 )');
    updateSuiyunGeju(index, 0);
}

// 更新流年柱
function updateLiunianPillars(dayunIndex) {
    const container = document.getElementById('liunian-pillar-container');
    if (!container) return;

    // 數據驗證
    if (!window.liunianByDayun || !window.liunianByDayun[dayunIndex]) {
        console.error('[JS 錯誤] window.liunianByDayun[' + dayunIndex + '] 為空');
        container.innerHTML = '<span class="text-stone-400 text-sm">流年數據缺失</span>';
        return;
    }

    if (!window.dayunData || window.dayunData.length === 0) {
        console.error('[JS 錯誤] window.dayunData 為空或長度為 0');
        container.innerHTML = '<span class="text-stone-400 text-sm">大運數據缺失</span>';
        return;
    }

    // 獲取該大運對應的 10 個流年
    const liunianList = window.liunianByDayun[dayunIndex];
    container.innerHTML = '';

    for (let i = 0; i < 10; i++) {
        const lnData = liunianList[i];
        if (!lnData) continue;

        const div = document.createElement('div');
        div.className = 'liunian-pillar-select cursor-pointer pillar-card flex flex-col items-center gap-1 p-2 rounded-xl border min-w-[80px] transition-all ' + (i === 0 ? 'border-indigo-500 bg-indigo-50' : 'border-stone-200 bg-stone-50 hover:bg-stone-100');
        div.onclick = function() { selectLiunian(i); };

        const ganWX = ganWuXing[lnData['流年天干']] || '土';
        const zhiWX = zhiWuXing[lnData['流年地支']] || '土';
        const ganColor = wuXingColors[ganWX];
        const zhiColor = wuXingColors[zhiWX];

        // 生成藏干 HTML
        let cangganHtml = '';
        const canggan = lnData['藏干'] || {};
        if (canggan['主氣'] && canggan['主氣']['干']) {
            const mainGan = canggan['主氣']['干'];
            const mainWX = ganWuXing[mainGan] || '土';
            const mainClass = wuXingColors[mainWX];
            cangganHtml += `<div class="flex justify-between text-[9px] w-full px-1 opacity-70"><span class="${mainClass.text}">${mainGan}</span><span class="text-stone-400">${canggan['主氣']['十神'] || ''}</span></div>`;
        }
        if (canggan['中氣'] && canggan['中氣']['干']) {
            const midGan = canggan['中氣']['干'];
            const midWX = ganWuXing[midGan] || '土';
            const midClass = wuXingColors[midWX];
            cangganHtml += `<div class="flex justify-between text-[9px] w-full px-1 opacity-70"><span class="${midClass.text}">${midGan}</span><span class="text-stone-400">${canggan['中氣']['十神'] || ''}</span></div>`;
        }
        if (canggan['餘氣'] && canggan['餘氣']['干']) {
            const restGan = canggan['餘氣']['干'];
            const restWX = ganWuXing[restGan] || '土';
            const restClass = wuXingColors[restWX];
            cangganHtml += `<div class="flex justify-between text-[9px] w-full px-1 opacity-70"><span class="${restClass.text}">${restGan}</span><span class="text-stone-400">${canggan['餘氣']['十神'] || ''}</span></div>`;
        }

        div.innerHTML = `
            <span class="text-[10px] text-stone-500 h-4">${lnData['流年十神']}</span>
            <div class="w-10 h-10 flex items-center justify-center text-2xl font-serif font-bold rounded-full ${ganColor.bg} ${ganColor.text} border-2 ${ganColor.border}">
                ${lnData['流年天干']}
            </div>
            <div class="w-10 h-10 flex items-center justify-center text-2xl font-serif font-bold ${zhiColor.text}">
                ${lnData['流年地支']}
            </div>
            <div class="flex flex-col gap-0.5 mt-1 items-center w-full min-h-[3.2rem]" id="liunian-${i}-canggan">
                ${cangganHtml}
            </div>
        `;
        container.appendChild(div);
    }

    // 默認選擇第一個流年
    currentLiunianIndex = 0;
    updateLiunianDisplay(0);

    // 更新流年判斷區域
    updateLiunianJudgment(dayunIndex);
}

// 更新流年判斷區域（顯示該大運的 10 個流年分析）
function updateLiunianJudgment(dayunIndex) {
    // 只更新整合分析中的容器
    const container = document.getElementById('liunian-judgment-container-integrated');
    if (!container) return;

    // 從 window.liunianByDayun 獲取該大運的 10 個流年
    const liunianList = window.liunianByDayun ? window.liunianByDayun[dayunIndex] : null;
    if (!liunianList || liunianList.length === 0) {
        container.innerHTML = '<span class="text-stone-400 text-sm col-span-2">流年數據缺失</span>';
        return;
    }

    let html = '';
    for (let i = 0; i < 10; i++) {
        const lnData = liunianList[i];
        if (!lnData) continue;

        const nianName = lnData['流年天干'] + lnData['流年地支'];
        const nianShiShen = lnData['流年十神'] || '';
        const nianDesc = lnData['格局影響'] || '平穩';
        const xuSui = lnData['虛歲'] || 0;

        let gejuClass = 'text-stone-600';
        if (nianDesc.includes('用神') || nianDesc.includes('喜神')) {
            gejuClass = 'text-green-600';
        } else if (nianDesc.includes('忌神')) {
            gejuClass = 'text-red-600';
        }

        html += `
        <div class="p-3 rounded-lg bg-stone-50 border border-stone-200">
            <div class="text-xs font-bold text-stone-600 mb-1">${nianName} (${nianShiShen}) <span class="text-stone-400 font-normal">虛歲${xuSui}</span></div>
            <div class="text-xs ${gejuClass} mt-1">${nianDesc}</div>
        </div>
        `;
    }
    container.innerHTML = html;
}

// 更新流月柱
function updateLiuyuePillars(dayunIndex) {
    const container = document.getElementById('liuyue-pillar-container');
    if (!container) return;

    // 獲取當前流年
    const liunianList = window.liuyueByLiunian && window.liuyueByLiunian[dayunIndex]
        ? window.liuyueByLiunian[dayunIndex][currentLiunianIndex]
        : null;

    if (!liunianList || liunianList.length === 0) {
        console.error('[JS 錯誤] window.liuyueByLiunian[' + dayunIndex + '][' + currentLiunianIndex + '] 為空');
        container.innerHTML = '<span class="text-stone-400 text-sm">流月數據缺失</span>';
        return;
    }

    container.innerHTML = '';

    for (let i = 0; i < 12; i++) {
        const lyData = liunianList[i];
        if (!lyData) continue;

        const div = document.createElement('div');
        div.className = 'liuyue-pillar-select cursor-pointer pillar-card flex flex-col items-center gap-1 p-2 rounded-xl border min-w-[80px] transition-all ' + (i === 0 ? 'border-indigo-500 bg-indigo-50' : 'border-stone-200 bg-stone-50 hover:bg-stone-100');
        div.onclick = function() { selectLiuyue(i); };

        const ganWX = ganWuXing[lyData['流月天干']] || '土';
        const zhiWX = zhiWuXing[lyData['流月地支']] || '土';
        const ganColor = wuXingColors[ganWX];
        const zhiColor = wuXingColors[zhiWX];

        // 生成藏干 HTML
        let cangganHtml = '';
        const canggan = lyData['藏干'] || {};
        if (canggan['主氣'] && canggan['主氣']['干']) {
            const mainGan = canggan['主氣']['干'];
            const mainWX = ganWuXing[mainGan] || '土';
            const mainClass = wuXingColors[mainWX];
            cangganHtml += `<div class="flex justify-between text-[9px] w-full px-1 opacity-70"><span class="${mainClass.text}">${mainGan}</span><span class="text-stone-400">${canggan['主氣']['十神'] || ''}</span></div>`;
        }
        if (canggan['中氣'] && canggan['中氣']['干']) {
            const midGan = canggan['中氣']['干'];
            const midWX = ganWuXing[midGan] || '土';
            const midClass = wuXingColors[midWX];
            cangganHtml += `<div class="flex justify-between text-[9px] w-full px-1 opacity-70"><span class="${midClass.text}">${midGan}</span><span class="text-stone-400">${canggan['中氣']['十神'] || ''}</span></div>`;
        }
        if (canggan['餘氣'] && canggan['餘氣']['干']) {
            const restGan = canggan['餘氣']['干'];
            const restWX = ganWuXing[restGan] || '土';
            const restClass = wuXingColors[restWX];
            cangganHtml += `<div class="flex justify-between text-[9px] w-full px-1 opacity-70"><span class="${restClass.text}">${restGan}</span><span class="text-stone-400">${canggan['餘氣']['十神'] || ''}</span></div>`;
        }

        div.innerHTML = `
            <span class="text-[10px] text-stone-500 h-4">${lyData['月份']}</span>
            <div class="w-10 h-10 flex items-center justify-center text-2xl font-serif font-bold rounded-full ${ganColor.bg} ${ganColor.text} border-2 ${ganColor.border}">
                ${lyData['流月天干']}
            </div>
            <div class="w-10 h-10 flex items-center justify-center text-2xl font-serif font-bold ${zhiColor.text}">
                ${lyData['流月地支']}
            </div>
            <div class="flex flex-col gap-0.5 mt-1 items-center w-full min-h-[3.2rem]" id="liuyue-${i}-canggan">
                ${cangganHtml}
            </div>
        `;
        container.appendChild(div);
    }

    // 默認選擇第一個流月
    currentLiuyueIndex = 0;
    updateLiuyueDisplay(0);
}

// 選擇流月
function selectLiuyue(index) {
    currentLiuyueIndex = index;

    // 更新流月選擇樣式
    document.querySelectorAll('.liuyue-pillar-select').forEach((item, idx) => {
        if (idx === index) {
            item.classList.add('border-indigo-500', 'bg-indigo-50');
            item.classList.remove('border-stone-200', 'bg-stone-50');
        } else {
            item.classList.remove('border-indigo-500', 'bg-indigo-50');
            item.classList.add('border-stone-200', 'bg-stone-50');
        }
    });

    updateLiuyueDisplay(index);
    updateZhiRelations();
    updateTianGanWuHe();
}

// 更新流月顯示
function updateLiuyueDisplay(index) {
    const dayunIndex = currentDayunIndex;
    const liunianList = window.liuyueByLiunian && window.liuyueByLiunian[dayunIndex]
        ? window.liuyueByLiunian[dayunIndex][currentLiunianIndex]
        : null;
    const lyData = liunianList ? liunianList[index] : null;
    if (!lyData) return;

    const ganWX = ganWuXing[lyData['流月天干']] || '土';
    const zhiWX = zhiWuXing[lyData['流月地支']] || '土';
    const ganColor = wuXingColors[ganWX];
    const zhiColor = wuXingColors[zhiWX];

    // 更新流月天干（帶五行顏色）
    const ganEl = document.getElementById('current-liuyue-gan');
    ganEl.textContent = lyData['流月天干'];
    ganEl.className = `w-11 h-11 flex items-center justify-center text-2xl font-serif font-bold rounded-full ${ganColor.bg} ${ganColor.text} border-2 ${ganColor.border}`;

    // 更新流月地支（帶五行顏色）
    const zhiEl = document.getElementById('current-liuyue-zhi');
    zhiEl.textContent = lyData['流月地支'];
    zhiEl.className = `w-11 h-11 flex items-center justify-center text-2xl font-serif font-bold ${zhiColor.text}`;

    document.getElementById('current-liuyue-shishen').textContent = lyData['流月十神'];

    // 更新流月藏干
    const canggan = lyData['藏干'] || {};
    let cangganHtml = '';
    if (canggan['主氣'] && canggan['主氣']['干']) {
        const mainGan = canggan['主氣']['干'];
        const mainWX = ganWuXing[mainGan] || '土';
        const mainClass = wuXingColors[mainWX];
        cangganHtml += `<div class="flex justify-between text-[9px] w-full px-1 opacity-70"><span class="${mainClass.text}">${mainGan}</span><span class="text-stone-400">${canggan['主氣']['十神'] || ''}</span></div>`;
    }
    if (canggan['中氣'] && canggan['中氣']['干']) {
        const midGan = canggan['中氣']['干'];
        const midWX = ganWuXing[midGan] || '土';
        const midClass = wuXingColors[midWX];
        cangganHtml += `<div class="flex justify-between text-[9px] w-full px-1 opacity-70"><span class="${midClass.text}">${midGan}</span><span class="text-stone-400">${canggan['中氣']['十神'] || ''}</span></div>`;
    }
    if (canggan['餘氣'] && canggan['餘氣']['干']) {
        const restGan = canggan['餘氣']['干'];
        const restWX = ganWuXing[restGan] || '土';
        const restClass = wuXingColors[restWX];
        cangganHtml += `<div class="flex justify-between text-[9px] w-full px-1 opacity-70"><span class="${restClass.text}">${restGan}</span><span class="text-stone-400">${canggan['餘氣']['十神'] || ''}</span></div>`;
    }
    document.getElementById('current-liuyue-canggan').innerHTML = cangganHtml;

    // 更新流月十二長生
    document.getElementById('current-liuyue-changsheng').textContent = lyData['十二長生'] || '';
}

// 選擇流年
function selectLiunian(index) {
    console.log('[selectLiunian] 點擊流年索引:', index);
    currentLiunianIndex = index;
    console.log('[selectLiunian] currentLiunianIndex 已設置為:', currentLiunianIndex);
    console.log('[selectLiunian] currentDayunIndex:', currentDayunIndex);

    // 更新流年選擇樣式
    document.querySelectorAll('.liunian-pillar-select').forEach((item, idx) => {
        if (idx === index) {
            item.classList.add('border-indigo-500', 'bg-indigo-50');
            item.classList.remove('border-stone-200', 'bg-stone-50');
        } else {
            item.classList.remove('border-indigo-500', 'bg-indigo-50');
            item.classList.add('border-stone-200', 'bg-stone-50');
        }
    });

    updateLiunianDisplay(index);

    // 更新流月（ resetting 為第一個流月）
    updateLiuyuePillars(currentDayunIndex);

    updateZhiRelations();
    updateTianGanWuHe();

    // 更新歲運格局
    console.log('[selectLiunian] 調用 updateSuiyunGeju(', currentDayunIndex, ',', index, ')');
    updateSuiyunGeju(currentDayunIndex, index);
}

// 更新流年顯示
function updateLiunianDisplay(index) {
    const dayunIndex = currentDayunIndex;
    // 使用 liunianByDayun 數據而非 allLiunianData
    const liunianList = window.liunianByDayun ? window.liunianByDayun[dayunIndex] : null;
    const lnData = liunianList ? liunianList[index] : null;
    if (!lnData) return;

    document.getElementById('current-liunian-gan').textContent = lnData['流年天干'];
    document.getElementById('current-liunian-zhi').textContent = lnData['流年地支'];
    document.getElementById('current-liunian-shishen').textContent = lnData['流年十神'];

    // 更新流年藏干
    const canggan = lnData['藏干'] || {};
    let cangganHtml = '';
    if (canggan['主氣'] && canggan['主氣']['干']) {
        const mainGan = canggan['主氣']['干'];
        const mainWX = ganWuXing[mainGan] || '土';
        const mainClass = wuXingColors[mainWX];
        cangganHtml += `<div class="flex justify-between text-[9px] w-full px-1 opacity-70"><span class="${mainClass.text}">${mainGan}</span><span class="text-stone-400">${canggan['主氣']['十神'] || ''}</span></div>`;
    }
    if (canggan['中氣'] && canggan['中氣']['干']) {
        const midGan = canggan['中氣']['干'];
        const midWX = ganWuXing[midGan] || '土';
        const midClass = wuXingColors[midWX];
        cangganHtml += `<div class="flex justify-between text-[9px] w-full px-1 opacity-70"><span class="${midClass.text}">${midGan}</span><span class="text-stone-400">${canggan['中氣']['十神'] || ''}</span></div>`;
    }
    if (canggan['餘氣'] && canggan['餘氣']['干']) {
        const restGan = canggan['餘氣']['干'];
        const restWX = ganWuXing[restGan] || '土';
        const restClass = wuXingColors[restWX];
        cangganHtml += `<div class="flex justify-between text-[9px] w-full px-1 opacity-70"><span class="${restClass.text}">${restGan}</span><span class="text-stone-400">${canggan['餘氣']['十神'] || ''}</span></div>`;
    }
    document.getElementById('current-liunian-canggan').innerHTML = cangganHtml;

    // 更新流年十二長生
    document.getElementById('current-liunian-changsheng').textContent = lnData['十二長生'] || '';
}

// 獲取兩個地支的關係
function getZhiRelation(zhi1, zhi2, allZhis = []) {
    if (!zhi1 || !zhi2) return null;
    if (zhi1 === zhi2) return { zhi: zhi2, type: '比和' };

    // 六合
    for (const he of zhiHe['六合']) {
        if ((he[0] === zhi1 && he[1] === zhi2) || (he[0] === zhi2 && he[1] === zhi1)) {
            return { zhi: zhi2, type: '合' };
        }
    }

    // 三合局
    for (const he of zhiHe['三合局']) {
        if (he.includes(zhi1) && he.includes(zhi2)) {
            return { zhi: zhi2, type: '局' };
        }
    }

    // 三會方
    for (const he of zhiHe['三會方']) {
        if (he.includes(zhi1) && he.includes(zhi2)) {
            return { zhi: zhi2, type: '會' };
        }
    }

    // 六沖
    const chongPairs = [['子','午'], ['丑','未'], ['寅','申'], ['卯','酉'], ['辰','戌'], ['巳','亥']];
    for (const pair of chongPairs) {
        if ((pair[0] === zhi1 && pair[1] === zhi2) || (pair[0] === zhi2 && pair[1] === zhi1)) {
            return { zhi: zhi2, type: '沖' };
        }
    }

    // 刑
    const sanXingGroups = [
        ['丑', '戌', '未'],  // 恃勢之刑
        ['寅', '巳', '申']   // 無恩之刑
    ];
    const ziXing = ['辰', '午', '酉', '亥'];  // 自刑
    const wuLiXing = ['子', '卯'];  // 無禮之刑

    // 檢查自刑
    if (ziXing.includes(zhi1) && zhi1 === zhi2) {
        return { zhi: zhi2, type: '刑' };
    }

    // 檢查無禮之刑
    if (wuLiXing.includes(zhi1) && wuLiXing.includes(zhi2) && zhi1 !== zhi2) {
        return { zhi: zhi2, type: '刑' };
    }

    // 檢查三刑
    for (const group of sanXingGroups) {
        if (group.includes(zhi1) && group.includes(zhi2)) {
            const hasAllThree = group.every(z => allZhis.includes(z));
            if (hasAllThree) {
                return { zhi: zhi2, type: '刑' };
            }
        }
    }

    // 穿
    const chuanPairs = [['子','未'], ['未','子'], ['丑','午'], ['午','丑'], ['寅','巳'], ['巳','寅'], ['卯','辰'], ['辰','卯'], ['申','亥'], ['亥','申'], ['酉','戌'], ['戌','酉']];
    for (const pair of chuanPairs) {
        if ((pair[0] === zhi1 && pair[1] === zhi2) || (pair[0] === zhi2 && pair[1] === zhi1)) {
            return { zhi: zhi2, type: '穿' };
        }
    }

    // 破
    const poPairs = [['子','酉'], ['酉','子'], ['丑','辰'], ['辰','丑'], ['寅','亥'], ['亥','寅'], ['卯','午'], ['午','卯'], ['未','申'], ['申','未'], ['巳','戌'], ['戌','巳']];
    for (const pair of poPairs) {
        if ((pair[0] === zhi1 && pair[1] === zhi2) || (pair[0] === zhi2 && pair[1] === zhi1)) {
            return { zhi: zhi2, type: '破' };
        }
    }

    return null;
}

// 更新大運流年沖刑穿破
function updateZhiRelations() {
    const container = document.getElementById('dy-ln-zhi-relations');
    if (!container) return;

    // 數據驗證
    if (!window.dayunData || window.dayunData.length === 0) {
        console.error('[JS 錯誤] window.dayunData 為空');
        container.innerHTML = '<span class="text-stone-400 text-sm">大運數據缺失</span>';
        return;
    }

    if (!window.allLiunianData || window.allLiunianData.length === 0) {
        console.error('[JS 錯誤] window.allLiunianData 為空');
        container.innerHTML = '<span class="text-stone-400 text-sm">流年數據缺失</span>';
        return;
    }

    if (!window.fourPillars || window.fourPillars.length === 0) {
        console.error('[JS 錯誤] window.fourPillars 為空');
        container.innerHTML = '<span class="text-stone-400 text-sm">四柱數據缺失</span>';
        return;
    }

    const dayunIndex = currentDayunIndex;
    const liunianIndex = currentLiunianIndex;

    // 使用 liunianByDayun 數據源
    const liunianList = window.liunianByDayun ? window.liunianByDayun[dayunIndex] : null;

    if (!window.dayunData[dayunIndex] || !liunianList || !liunianList[liunianIndex]) {
        console.error('[JS 錯誤] 大運或流年數據索引超出範圍');
        container.innerHTML = '<span class="text-stone-400 text-sm">數據索引錯誤</span>';
        return;
    }

    const dayunZhi = window.dayunData[dayunIndex]['大運支'];
    const liunianZhi = liunianList[liunianIndex]['流年地支'];

    // 四柱地支
    const pillarsZhi = window.fourPillars.map(p => p.charAt(1));
    const pillarNames = ['年', '月', '日', '時'];

    // 收集所有相关地支
    const allZhis = [dayunZhi, liunianZhi, ...pillarsZhi];

    let html = '';

    // 三刑
    const hasChouXuWei = allZhis.includes('丑') && allZhis.includes('戌') && allZhis.includes('未');
    if (hasChouXuWei) {
        html += '<span class="px-3 py-2 rounded-lg text-sm border bg-red-50 text-red-700 border-red-200 font-medium">恃勢之刑 (丑戌未)</span>';
    }

    const hasYinSiShen = allZhis.includes('寅') && allZhis.includes('巳') && allZhis.includes('申');
    if (hasYinSiShen) {
        html += '<span class="px-3 py-2 rounded-lg text-sm border bg-red-50 text-red-700 border-red-200 font-medium">無恩之刑 (寅巳申)</span>';
    }

    // 無禮之刑
    if (allZhis.includes('子') && allZhis.includes('卯')) {
        html += '<span class="px-3 py-2 rounded-lg text-sm border bg-red-50 text-red-700 border-red-200 font-medium">無禮之刑 (子卯)</span>';
    }

    // 自刑
    const ziXingZhi = ['辰', '午', '酉', '亥'];
    ziXingZhi.forEach(z => {
        const count = allZhis.filter(x => x === z).length;
        if (count >= 2) {
            html += `<span class="px-3 py-2 rounded-lg text-sm border bg-red-50 text-red-700 border-red-200 font-medium">自刑 (${z}${z})</span>`;
        }
    });

    // 大運與流年沖穿破
    const dyLnChong = getZhiRelation(dayunZhi, liunianZhi, allZhis);
    if (dyLnChong && dyLnChong.type === '沖') {
        html += `<span class="px-3 py-2 rounded-lg text-sm border bg-red-50 text-red-700 border-red-200 font-medium">${dayunZhi}沖${liunianZhi}</span>`;
    }
    if (dyLnChong && dyLnChong.type === '穿') {
        html += `<span class="px-3 py-2 rounded-lg text-sm border bg-red-50 text-red-700 border-red-200 font-medium">${dayunZhi}穿${liunianZhi}</span>`;
    }
    if (dyLnChong && dyLnChong.type === '破') {
        html += `<span class="px-3 py-2 rounded-lg text-sm border bg-red-50 text-red-700 border-red-200 font-medium">${dayunZhi}破${liunianZhi}</span>`;
    }

    // 大運與四柱沖穿破
    pillarsZhi.forEach((zhi, idx) => {
        const rel = getZhiRelation(dayunZhi, zhi, allZhis);
        if (rel && rel.type === '沖') {
            html += `<span class="px-3 py-2 rounded-lg text-sm border bg-red-50 text-red-700 border-red-200 font-medium">大運沖${pillarNames[idx]}(${zhi})</span>`;
        }
        if (rel && rel.type === '穿') {
            html += `<span class="px-3 py-2 rounded-lg text-sm border bg-red-50 text-red-700 border-red-200 font-medium">大運穿${pillarNames[idx]}(${zhi})</span>`;
        }
        if (rel && rel.type === '破') {
            html += `<span class="px-3 py-2 rounded-lg text-sm border bg-red-50 text-red-700 border-red-200 font-medium">大運破${pillarNames[idx]}(${zhi})</span>`;
        }
    });

    // 流年與四柱沖穿破
    pillarsZhi.forEach((zhi, idx) => {
        const rel = getZhiRelation(liunianZhi, zhi, allZhis);
        if (rel && rel.type === '沖') {
            html += `<span class="px-3 py-2 rounded-lg text-sm border bg-red-50 text-red-700 border-red-200 font-medium">流年沖${pillarNames[idx]}(${zhi})</span>`;
        }
        if (rel && rel.type === '穿') {
            html += `<span class="px-3 py-2 rounded-lg text-sm border bg-red-50 text-red-700 border-red-200 font-medium">流年穿${pillarNames[idx]}(${zhi})</span>`;
        }
        if (rel && rel.type === '破') {
            html += `<span class="px-3 py-2 rounded-lg text-sm border bg-red-50 text-red-700 border-red-200 font-medium">流年破${pillarNames[idx]}(${zhi})</span>`;
        }
    });

    if (!html) html = '<span class="text-stone-400 text-sm">無沖刑穿破</span>';

    container.innerHTML = html;
}

// 更新天干五合
function updateTianGanWuHe() {
    const container = document.getElementById('tian-gan-wu-he');
    if (!container) return;

    // 數據驗證
    if (!window.dayunData || window.dayunData.length === 0) {
        console.error('[JS 錯誤] window.dayunData 為空');
        container.innerHTML = '<span class="text-stone-400 text-sm">大運數據缺失</span>';
        return;
    }

    if (!window.allLiunianData || window.allLiunianData.length === 0) {
        console.error('[JS 錯誤] window.allLiunianData 為空');
        container.innerHTML = '<span class="text-stone-400 text-sm">流年數據缺失</span>';
        return;
    }

    if (!window.fourPillars || window.fourPillars.length === 0) {
        console.error('[JS 錯誤] window.fourPillars 為空');
        container.innerHTML = '<span class="text-stone-400 text-sm">四柱數據缺失</span>';
        return;
    }

    const dayunIndex = currentDayunIndex;
    const liunianIndex = currentLiunianIndex;

    // 使用 liunianByDayun 數據源
    const liunianList = window.liunianByDayun ? window.liunianByDayun[dayunIndex] : null;

    if (!window.dayunData[dayunIndex] || !liunianList || !liunianList[liunianIndex]) {
        console.error('[JS 錯誤] 大運或流年數據索引超出範圍');
        container.innerHTML = '<span class="text-stone-400 text-sm">數據索引錯誤</span>';
        return;
    }

    const dayunGan = window.dayunData[dayunIndex]['大運干'];
    const liunianGan = liunianList[liunianIndex]['流年天干'];

    // 提取四柱天干
    const pillarsGan = window.fourPillars.map(p => p.charAt(0));
    const pillarNames = ['年', '月', '日', '時'];

    let html = '';

    // 四柱原本的天干五合
    const checkedPairs = new Set();
    for (let i = 0; i < 4; i++) {
        for (let j = i + 1; j < 4; j++) {
            const gan1 = pillarsGan[i];
            const gan2 = pillarsGan[j];
            const pairKey = gan1 < gan2 ? gan1 + gan2 : gan2 + gan1;
            if (!checkedPairs.has(pairKey) && tianGanHe[gan1] === gan2) {
                checkedPairs.add(pairKey);
                html += `<span class="px-3 py-2 rounded-lg text-sm border bg-blue-50 text-blue-700 border-blue-200 font-medium">${gan1}合${gan2} (四柱)</span>`;
            }
        }
    }

    // 大運與四柱五合
    pillarsGan.forEach((gan) => {
        if (tianGanHe[dayunGan] === gan) {
            html += `<span class="px-2 py-1 rounded text-xs border bg-green-50 text-green-700 border-green-200">大運${gan}合${dayunGan}</span>`;
        }
    });

    // 流年與四柱五合
    pillarsGan.forEach((gan) => {
        if (tianGanHe[liunianGan] === gan) {
            html += `<span class="px-2 py-1 rounded text-xs border bg-green-50 text-green-700 border-green-200">流年${gan}合${liunianGan}</span>`;
        }
    });

    if (!html) html = '<span class="text-stone-400 text-sm">無五合</span>';

    container.innerHTML = html;
}

// 更新歲運格局顯示
function updateSuiyunGeju(dayunIndex, liunianIndex) {
    console.log('[歲運格局] 更新：dayunIndex=' + dayunIndex + ', liunianIndex=' + liunianIndex);
    console.log('[歲運格局] window.suiyunGejuAll:', window.suiyunGejuAll ? '存在，長度=' + window.suiyunGejuAll.length : '不存在');

    // 數據驗證
    if (!window.suiyunGejuAll || !Array.isArray(window.suiyunGejuAll)) {
        console.error('[JS 錯誤] window.suiyunGejuAll 為空或不是數組');
        return;
    }

    // 查找對應的歲運格局數據
    const suiyunData = window.suiyunGejuAll.find(
        item => item.dayun_index === dayunIndex && item.liunian_index === liunianIndex
    );

    if (!suiyunData) {
        console.warn('[歲運格局] 未找到對應數據 - dayunIndex=' + dayunIndex + ', liunianIndex=' + liunianIndex);
        // 嘗試查找該大運的第一個流年數據
        const fallbackData = window.suiyunGejuAll.find(item => item.dayun_index === dayunIndex && item.liunian_index === 0);
        if (fallbackData) {
            console.log('[歲運格局] 使用備用數據 (liunian_index=0):', fallbackData);
        }
        console.log('[歲運格局] 可用的數據:', window.suiyunGejuAll.slice(0, 3));
        return;
    }

    if (!suiyunData.sui_yun_ge_ju) {
        console.warn('[歲運格局] sui_yun_ge_ju 為空');
        return;
    }

    const geju = suiyunData.sui_yun_ge_ju;
    console.log('[歲運格局] 找到數據:', geju);

    // 更新歲運狀態
    const statusEl = document.getElementById('suiyun-status-display');
    console.log('[歲運格局] statusEl:', statusEl ? '找到' : '未找到');
    if (statusEl) {
        statusEl.textContent = geju['歲運格局狀態'] || '無';
        statusEl.className = 'font-medium ' + (
            geju['歲運格局狀態'] === '成格' ? 'text-green-600' :
            geju['歲運格局狀態'] === '破格' ? 'text-red-600' : 'text-stone-600'
        );
    }

    // 更新綜合判斷
    const zongheEl = document.getElementById('suiyun-zonghe-display');
    if (zongheEl) {
        zongheEl.textContent = geju['綜合判斷'] || '無特殊影響';
    }

    // 更新斷語
    const duanyuEl = document.getElementById('suiyun-duanyu-display');
    if (duanyuEl) {
        duanyuEl.textContent = geju['斷語'] || '';
    }

    // 更新應事
    const yingshiContainer = document.getElementById('suiyun-yingshi-container');
    if (yingshiContainer) {
        const yingshiList = geju['應事'] || [];
        if (yingshiList && yingshiList.length > 0) {
            yingshiContainer.style.display = 'block';
            yingshiContainer.innerHTML = `
                <div class="text-xs text-indigo-600 font-medium mb-2">應事</div>
                <div class="flex flex-wrap gap-2">
                    ${yingshiList.map(ying => `<span class="px-3 py-1.5 rounded-lg bg-white border border-indigo-200 text-indigo-700 text-sm">${ying}</span>`).join('')}
                </div>
            `;
        } else {
            yingshiContainer.style.display = 'none';
        }
    }

    console.log('[歲運格局] 更新成功');
}
