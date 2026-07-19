#!/usr/bin/env python3
"""将 DDS/TGA 图标批量转换为 PNG 并按中文国家名分类"""

import os
import re
import struct
from PIL import Image
from collections import defaultdict

# ========== 国家代码到中文名映射 ==========
COUNTRY_CN = {
    # ---- 亚洲 ----
    'AFG': '阿富汗',
    'ARM': '亚美尼亚',
    'AZD': '阿塞拜疆',
    'AZR': '阿塞拜疆',
    'BAN': '孟加拉',
    'BHU': '不丹',
    'BUK': '布哈拉',
    'BUR': '缅甸',
    'CAM': '柬埔寨',
    'CHI': '中国',
    'CHL': '中国',
    'CHC': '中共',
    'CSR': '中华苏维埃共和国',
    'CTL': '中华民国',
    'BRI': '英属印度',
    'DEL': '德里',
    'DIC': '印度',
    'GXC': '广西',
    'GUI': '几内亚',
    'GUJ': '古吉拉特',
    'HEJ': '黑龙江',
    'HNN': '湖南',
    'HUB': '湖北',
    'HYD': '海得拉巴',
    'IDA': '印度尼西亚',
    'IKA': '印度',
    'IND': '印度',
    'INM': '英属马来亚',
    'INS': '荷属东印度',
    'JAP': '日本',
    'JIA': '江苏',
    'JIL': '吉林',
    'JKR': '交趾支那',
    'KAZ': '哈萨克斯坦',
    'KHI': '希瓦',
    'KKK': '高加索',
    'KOR': '朝鲜',
    'KUB': '库班',
    'KYR': '吉尔吉斯斯坦',
    'LAO': '老挝',
    'LEM': '黎凡特',
    'MAK': '澳门',
    'MAL': '马来亚',
    'MAN': '满洲国',
    'MEN': '蒙古',
    'MNA': '马尼拉',
    'MNS': '蒙古',
    'MNT': '蒙古',
    'MON': '蒙古',
    'NEP': '尼泊尔',
    'SIA': '暹罗',
    'SIK': '锡金',
    'SHX': '山西',
    'SHC': '山东',
    'SHD': '山东',
    'SND': '信德',
    'TAN': '坦努图瓦',
    'TIB': '西藏',
    'TGS': '外蒙古',
    'TUR': '土耳其',
    'YNC': '云南',
    'YEM': '也门',
    'ZAN': '桑给巴尔',
    'ZHE': '浙江',
    'ZHL': '直隶',
    'ZIC': '四川',

    # ---- 欧洲 ----
    'ALB': '阿尔巴尼亚',
    'ANC': '安哥拉',
    'AST': '奥地利',
    'AUS': '澳大利亚',
    'BAV': '巴伐利亚',
    'BEL': '比利时',
    'BLR': '白俄罗斯',
    'BOS': '波斯尼亚',
    'BUL': '保加利亚',
    'CBT': '喀尔巴阡',
    'CRO': '克罗地亚',
    'CZE': '捷克',
    'DEN': '丹麦',
    'DNZ': '但泽',
    'ENG': '英格兰',
    'EST': '爱沙尼亚',
    'FIN': '芬兰',
    'FRA': '法兰西共和国',
    'FRR': '法兰西',
    'FSR': '法兰西',
    'GEO': '格鲁吉亚',
    'GER': '德意志帝国',
    'GRE': '希腊',
    'HOL': '荷兰',
    'HUN': '匈牙利',
    'IRE': '爱尔兰',
    'ITA': '意大利',
    'ITM': '意大利',
    'ITS': '意大利社会共和国',
    'LAT': '拉脱维亚',
    'LIE': '列支敦士登',
    'LIT': '立陶宛',
    'LTG': '立陶宛',
    'LUB': '卢布林',
    'LUX': '卢森堡',
    'MDR': '摩尔达维亚',
    'MED': '地中海',
    'MON': '黑山',
    'NOR': '挪威',
    'OCC': '奥克西塔尼亚',
    'POL': '波兰',
    'POZ': '波兹南',
    'POR': '葡萄牙',
    'PRC': '普罗旺斯',
    'PRG': '布拉格',
    'PRU': '普鲁士',
    'ROM': '罗马尼亚',
    'RPT': '莱茵兰',
    'RUS': '俄罗斯',
    'SAK': '萨克森',
    'SAN': '圣马力诺',
    'SAR': '撒丁尼亚',
    'SER': '塞尔维亚',
    'SLO': '斯洛伐克',
    'SOV': '苏联',
    'SPR': '西班牙',
    'SWE': '瑞典',
    'SWI': '瑞士',
    'UKR': '乌克兰',
    'UNT': '联合王国',
    'URL': '乌拉尔',
    'UVS': '乌克兰苏维埃',
    'VAN': '瓦努阿图',
    'VAT': '梵蒂冈',
    'VCI': '维希法国',
    'VDW': '维希',
    'VEN': '威尼斯',
    'VNE': '威尼斯',
    'WAS': '华沙',
    'WLS': '威尔士',
    'WOL': '沃里尼亚',
    'WRD': '符腾堡',
    'WUK': '西乌克兰',
    'WVA': '西瓦',
    'YUG': '南斯拉夫',
    'ACF': '法兰西公社',
    'ADR': '安道尔',
    'ALT': '阿尔泰',
    'APW': '阿普利亚',
    'ASF': '阿尔萨斯-洛林',
    'ASY': '亚述',
    'BEA': '不列颠东亚',
    'BMD': '百慕大',
    'BNM': '波希米亚-摩拉维亚',
    'BNT': '班特',
    'BRE': '布列塔尼',
    'BSM': '比萨拉比亚',
    'BST': '巴斯克',
    'BWI': '英属西印度',
    'CAL': '加利福尼亚',
    'CEK': '捷克',
    'CFF': '中非联邦',
    'CIL': '西里西亚',
    'CLA': '加泰罗尼亚',
    'COU': '康沃尔',
    'CRS': '喀尔巴阡鲁塞尼亚',
    'DOA': '多瑙河',
    'DON': '顿河',
    'DSH': '达吉斯坦',
    'DUL': '杜兰线',
    'DZG': '但泽',
    'ELS': '阿尔萨斯',
    'EPR': '东普鲁士',
    'EQS': '赤道几内亚',
    'FBL': '弗兰德斯-布拉班特',
    'FEA': '远东共和国',
    'FER': '法兰西帝国',
    'FGB': '英属几内亚',
    'FNA': '法属北非',
    'FOC': '法兰西公社',
    'FRI': '弗里西亚',
    'FWG': '法属西非',
    'GDG': '格但斯克',
    'GFB': '德属波罗的海',
    'GLN': '加利西亚',
    'GRA': '格拉纳达',
    'HEL': '赫尔维蒂',
    'HRA': '海尔维第',
    'JAB': '亚布洛内茨',
    'JAZ': '亚速尔',
    'JBR': '吉布拉尔',
    'JGX': '晋西',
    'JMK': '牙买加',
    'KAR': '卡累利阿',
    'KLK': '卡尔梅克',
    'KMC': '克里米亚',
    'KMP': '堪察加',
    'KOE': '荷兰东印度公司',
    'KRK': '克拉科夫',
    'KSH': '克什米尔',
    'KUM': '库曼',
    'KUT': '库泰',
    'LBA': '利比亚',
    'LUS': '卢萨蒂亚',
    'MAZ': '马祖里',
    'MSC': '莫斯科',
    'MSL': '摩泽尔',
    'MSS': '梅克伦堡',
    'MUT': '米蒂亚',
    'NCT': '新喀里多尼亚',
    'NEE': '荷兰',
    'NFR': '北法兰西',
    'NGC': '新几内亚',
    'NIR': '北爱尔兰',
    'NMB': '北摩拉维亚',
    'NTS': '的里雅斯特',
    'NYC': '纽约',
    'OCG': '奥克西塔尼亚',
    'ORD': '敖德萨',
    'ORG': '奥廖尔',
    'ORI': '奥里萨',
    'OTY': '奥斯曼',
    'PBD': '波多利亚',
    'PLA': '波拉比亚',
    'PLF': '波兰自由邦',
    'PLS': '波利西亚',
    'PMG': '波美拉尼亚',
    'PNK': '平斯克',
    'QES': '喀山',
    'QMC': '魁北克',
    'QUN': '昆士兰',
    'RBR': '罗塞尼亚',
    'REH': '莱茵',
    'REK': '莱茵兰',
    'RHI': '莱茵兰',
    'RIF': '里夫共和国',
    'RMA': '罗马',
    'SBP': '塞尔维亚-波黑',
    'SDT': '南蒂罗尔',
    'SEA': '东南亚',
    'SIC': '西西里',
    'SKM': '斯基泰',
    'SMF': '萨莫吉希亚',
    'SRF': '南法兰西',
    'SRK': '萨哈共和国',
    'SUY': '苏里南',
    'TFE': '法属赤道非洲',
    'TMS': '特兰西瓦尼亚',
    'TRA': '外高加索',
    'TRV': '特兰西瓦尼亚',
    'TUS': '托斯卡纳',
    'TWR': '托伦',
    'URG': '乌拉圭',
    'VJV': '瓦尔纳',
    'XIK': '锡克',
    'XSR': '外高加索苏维埃',

    # ---- 非洲 ----
    'ARB': '阿拉伯',
    'BOT': '博茨瓦纳',
    'CMR': '喀麦隆',
    'COG': '刚果',
    'DJI': '吉布提',
    'EGY': '埃及',
    'ERI': '厄立特里亚',
    'ETH': '埃塞俄比亚',
    'KEN': '肯尼亚',
    'LBA': '利比亚',
    'LIB': '利比里亚',
    'MOR': '摩洛哥',
    'MSL': '莫桑比克',
    'NIG': '尼日利亚',
    'RHO': '罗德西亚',
    'SAF': '南非',
    'SOM': '索马里',
    'SUD': '苏丹',
    'TUN': '突尼斯',
    'UGA': '乌干达',
    'ZAN': '桑给巴尔',
    'ZIM': '津巴布韦',

    # ---- 北美洲 ----
    'ALA': '阿拉斯加',
    'CAL': '加利福尼亚',
    'CAN': '加拿大',
    'COS': '哥斯达黎加',
    'CUB': '古巴',
    'DOM': '多米尼加',
    'ELS': '萨尔瓦多',
    'GUA': '危地马拉',
    'HAI': '海地',
    'HBC': '哈德逊湾公司',
    'HON': '洪都拉斯',
    'MEX': '墨西哥',
    'NIC': '尼加拉瓜',
    'NFL': '纽芬兰',
    'NYC': '纽约',
    'PAN': '巴拿马',
    'QUE': '魁北克',
    'TEX': '德克萨斯',
    'USA': '美利坚合众国',
    'USP': '太平洋合众国',
    'WSH': '华盛顿',

    # ---- 南美洲 ----
    'ARG': '阿根廷',
    'BOL': '玻利维亚',
    'BRA': '巴西',
    'CHL': '智利',
    'COL': '哥伦比亚',
    'ECU': '厄瓜多尔',
    'PAR': '巴拉圭',
    'PEN': '秘鲁',
    'PER': '秘鲁',
    'URG': '乌拉圭',
    'VEN': '委内瑞拉',

    # ---- 大洋洲 ----
    'ANZ': '澳大拉西亚',
    'AUS': '澳大利亚',
    'FIJ': '斐济',
    'GIL': '吉尔伯特群岛',
    'NZL': '新西兰',
    'PAL': '帕劳',
    'SAM': '萨摩亚',
    'TGA': '汤加',
    'VAN': '瓦努阿图',

    # ---- 中东/中亚 ----
    'BHR': '巴林',
    'IRQ': '伊拉克',
    'ISR': '以色列',
    'JOR': '约旦',
    'KHO': '花剌子模',
    'KUR': '库尔德斯坦',
    'KUW': '科威特',
    'LEB': '黎巴嫩',
    'OMA': '阿曼',
    'PAL': '巴勒斯坦',
    'QAT': '卡塔尔',
    'SAU': '沙特阿拉伯',
    'SYR': '叙利亚',
    'TUR': '土耳其',
    'UAE': '阿联酋',
    'YEM': '也门',

    # ---- 南亚 ----
    'BHUT': '不丹',
    'CEY': '锡兰',
    'SIK': '锡克',
    'KSH': '克什米尔',

    # ---- 特殊/虚构 ----
    'ABK': '阿布哈兹',
    'KAL': '加里曼丹',
    'KUT': '库泰',
    'SRK': '萨哈共和国',
    'CBT': '喀尔巴阡',
    'TRV': '特兰西瓦尼亚',
    'PLS': '波利西亚',
    'PNK': '平斯克',
    'PBD': '波多利亚',
    'PLF': '波兰自由邦',
    'WUK': '西乌克兰',
    'BSM': '比萨拉比亚',
    'NIR': '北爱尔兰自由邦',
    'NIN': '尼日尔',
    'RIF': '里夫共和国',
    'XSR': '外高加索SFSR',
    'NMB': '北摩拉维亚',
    'NFR': '北法兰西',
    'SRF': '南法兰西',
    'FBL': '弗兰德斯-布拉班特',
    'BRE': '布列塔尼',
    'BRI': '不列颠',
    'OCC': '奥克西塔尼亚',
    'OCG': '奥克西塔尼亚',
    'COU': '康沃尔',
    'FRI': '弗里西亚',
    'POL': '波兰',
    'JOR': '约旦',
    'CSR': '中华苏维埃共和国',
    'SIA': '暹罗',
    'ROM': '罗马尼亚',
    'YUG': '南斯拉夫',
    'CSA': '美利坚联盟国',
    'NEE': '尼德兰',
    'AUS': '奥地利帝国',
    'BEL': '比利时',
    'BUL': '保加利亚',
    'CZE': '捷克',
    'DEN': '丹麦',
    'FIN': '芬兰',
    'FRA': '法兰西共和国',
    'GER': '德意志帝国',
    'GRE': '希腊',
    'HUN': '匈牙利',
    'ITA': '意大利王国',
    'JAP': '日本帝国',
    'NED': '荷兰',
    'NOR': '挪威',
    'POL': '波兰',
    'POR': '葡萄牙',
    'RUS': '俄罗斯共和国',
    'SPA': '西班牙',
    'SWE': '瑞典',
    'TUR': '奥斯曼帝国',
    'UK': '联合王国',
    'USA': '美国',
    'ASA': '阿萨姆',
    'BGI': '英属圭亚那',
    'BLY': '俾路支',
    'CCC': '中华民国（中共）',
    'FUJ': '福建',
    'PAK': '巴基斯坦',
    'PHI': '菲律宾',
    'PUN': '旁遮普',
    'RAJ': '英属印度',
    'SHA': '上海',
    'TNG': '汤加',
    'VIN': '文莱',
}

# 英文人名到中文的简单音译映射（常见名）
NAME_TRANSLATIONS = {
    'abdul': '阿卜杜勒', 'ahmed': '艾哈迈德', 'ali': '阿里', 'ahmad': '艾哈迈德',
    'amanullah': '阿曼努拉', 'khan': '汗', 'mohammed': '穆罕默德', 'nadir': '纳迪尔',
    'shah': '沙阿', 'wahab': '瓦哈布', 'wali': '瓦利', 'sardar': '萨达尔',
    'ghazi': '加齐', 'zaman': '扎曼', 'nabi': '纳比', 'ghulam': '古拉姆',
    'nestor': '涅斯托尔', 'lakoba': '拉科巴',
    'sebastian': '塞巴斯蒂安', 'faure': '福雷',
    'boris': '鲍里斯', 'skossyreff': '斯科瑟列夫',
    'justi': '朱斯蒂', 'guitart': '吉塔特',
    'charles': '查尔斯', 'curtis': '柯蒂斯', 'frank': '弗兰克', 'phillips': '菲利普斯', 'john': '约翰', 'franklin': '富兰克林',
    'aranitasi': '阿拉尼塔西', 'ferdinand': '费迪南', 'bourbon': '波旁', 'fevziu': '费夫齐乌',
    'gjergj': '杰尔吉', 'fishta': '菲什塔', 'kolonja': '科洛尼亚', 'leskoviku': '莱斯科维库',
    'mborja': '姆博里亚', 'myrdacz': '米尔达茨', 'noli': '诺利',
    'osman': '奥斯曼', 'rastoder': '拉斯托德尔', 'otto': '奥托', 'witte': '维特',
    'pandeli': '潘德利', 'cale': '查莱', 'pervizi': '佩尔维齐',
    'prince': '亲王', 'arthur': '亚瑟', 'kiril': '基里尔', 'oskar': '奥斯卡',
    'prishtina': '普里什蒂纳', 'provisional': '临时', 'council': '委员会',
    'sehzade': '谢赫扎德', 'mehmed': '穆罕默德', 'shkupi': '什库皮',
    'general': '将军', 'large': '', 'portrait': '肖像',
    'alexander': '亚历山大', 'alexei': '阿列克谢', 'andrei': '安德烈',
    'anna': '安娜', 'anton': '安东', 'antonio': '安东尼奥',
    'benito': '贝尼托', 'mussolini': '墨索里尼',
    'carlo': '卡洛', 'carlos': '卡洛斯',
    'david': '大卫', 'dimitri': '德米特里',
    'eduard': '爱德华', 'edward': '爱德华', 'elizabeth': '伊丽莎白',
    'francisco': '弗朗西斯科', 'franco': '佛朗哥', 'friedrich': '弗里德里希',
    'george': '乔治', 'giovanni': '乔瓦尼', 'gustav': '古斯塔夫',
    'hans': '汉斯', 'heinrich': '海因里希', 'henry': '亨利', 'hermann': '赫尔曼',
    'ivan': '伊万', 'joseph': '约瑟夫', 'juan': '胡安',
    'karl': '卡尔', 'konrad': '康拉德',
    'leon': '列昂', 'louis': '路易', 'ludwig': '路德维希',
    'manuel': '曼努埃尔', 'maria': '玛丽亚', 'mario': '马里奥',
    'maximilian': '马克西米利安', 'michael': '迈克尔', 'mikhail': '米哈伊尔',
    'napoleon': '拿破仑', 'nicholas': '尼古拉斯', 'nikolai': '尼古拉',
    'otto': '奥托', 'paul': '保罗', 'peter': '彼得', 'philippe': '菲利普',
    'raymond': '雷蒙德', 'richard': '理查德', 'robert': '罗伯特',
    'rudolf': '鲁道夫', 'stalin': '斯大林', 'stephen': '斯蒂芬',
    'theodore': '西奥多', 'thomas': '托马斯',
    'victor': '维克多', 'vladimir': '弗拉基米尔', 'wilhelm': '威廉',
    'william': '威廉', 'winston': '温斯顿', 'churchill': '丘吉尔',
    'hirohito': '裕仁', 'tojo': '东条', 'yamamoto': '山本',
    'hideki': '英机', 'isovoku': '五十六',
    'chiang': '蒋', 'kai-shek': '介石', 'mao': '毛', 'zedong': '泽东',
    'zhou': '周', 'enlai': '恩来',
    'sun': '孙', 'yat-sen': '中山', 'zhang': '张', 'zuolin': '作霖',
    'puyi': '溥仪', 'yuan': '袁', 'shikai': '世凯',
    'kemal': '凯末尔', 'ataturk': '阿塔图尔克',
    'lenin': '列宁', 'trotsky': '托洛茨基', 'bukharin': '布哈林',
    'zhukov': '朱可夫', 'rokossovsky': '罗科索夫斯基',
    'de_gaulle': '戴高乐', 'petain': '贝当', 'laval': '拉瓦尔',
    'hitler': '希特勒', 'goering': '戈林', 'himmler': '希姆莱',
    'rommel': '隆美尔', 'donitz': '邓尼茨',
    'roosevelt': '罗斯福', 'truman': '杜鲁门', 'eisenhower': '艾森豪威尔',
    'macarthur': '麦克阿瑟', 'patton': '巴顿', 'marshall': '马歇尔',
    'king': '金', 'president': '总统', 'minister': '部长',
    'prime': '首相', 'leader': '领袖', 'emperor': '皇帝',
    'tsar': '沙皇', 'czar': '沙皇', 'duke': '公爵', 'count': '伯爵',
    'baron': '男爵', 'lord': '勋爵', 'sir': '爵士',
}


def translate_name(filename):
    """将英文领袖文件名简单音译为中文"""
    # 去除扩展名和路径
    name = os.path.splitext(os.path.basename(filename))[0]
    # 去除国家代码前缀
    parts = name.split('_')
    if len(parts) > 1 and len(parts[0]) == 3 and parts[0].isupper():
        name = '_'.join(parts[1:])
    elif parts[0].lower().startswith('portrait'):
        name = '_'.join(parts[1:]) if len(parts) > 1 else name

    # 转换为小写并分词
    name_lower = name.lower()
    words = re.split(r'[_\- ]', name_lower)

    translated_parts = []
    for word in words:
        if word in ['dds', 'tga', 'png', 'jpg']:
            continue
        if word in NAME_TRANSLATIONS:
            translated_parts.append(NAME_TRANSLATIONS[word])
        elif word.isnumeric():
            translated_parts.append(word)
        else:
            translated_parts.append(word)

    # 过滤空字符串
    translated_parts = [p for p in translated_parts if p]
    if not translated_parts:
        return name
    return '_'.join(translated_parts)


def decode_dxt1(block_data, width, height):
    """解码 DXT1 (BC1) 压缩块为 RGBA 像素"""
    pixels = bytearray(width * height * 4)
    block_size = 4

    for by in range(0, height, block_size):
        for bx in range(0, width, block_size):
            block_idx = ((by // block_size) * (width // block_size) + (bx // block_size)) * 8
            if block_idx + 8 > len(block_data):
                continue

            c0 = struct.unpack_from('<H', block_data, block_idx)[0]
            c1 = struct.unpack_from('<H', block_data, block_idx + 2)[0]
            bits = struct.unpack_from('<I', block_data, block_idx + 4)[0]

            r0 = ((c0 >> 11) & 0x1F) * 255 // 31
            g0 = ((c0 >> 5) & 0x3F) * 255 // 63
            b0 = (c0 & 0x1F) * 255 // 31
            r1 = ((c1 >> 11) & 0x1F) * 255 // 31
            g1 = ((c1 >> 5) & 0x3F) * 255 // 63
            b1 = (c1 & 0x1F) * 255 // 31

            colors = [(r0, g0, b0, 255), (r1, g1, b1, 255)]
            if c0 > c1:
                colors.append(((2*r0 + r1) // 3, (2*g0 + g1) // 3, (2*b0 + b1) // 3, 255))
                colors.append(((r0 + 2*r1) // 3, (g0 + 2*g1) // 3, (b0 + 2*b1) // 3, 255))
            else:
                colors.append(((r0 + r1) // 2, (g0 + g1) // 2, (b0 + b1) // 2, 255))
                colors.append((0, 0, 0, 0))

            for i in range(16):
                px = bx + (i % 4)
                py = by + (i // 4)
                if px >= width or py >= height:
                    continue
                idx = (py * width + px) * 4
                code = (bits >> (i * 2)) & 3
                c = colors[code]
                pixels[idx:idx+4] = bytes(c)

    return Image.frombytes('RGBA', (width, height), bytes(pixels))


def decode_dxt5(block_data, width, height):
    """解码 DXT5 (BC3) 压缩块为 RGBA 像素"""
    pixels = bytearray(width * height * 4)
    block_size = 4

    for by in range(0, height, block_size):
        for bx in range(0, width, block_size):
            block_idx = ((by // block_size) * (width // block_size) + (bx // block_size)) * 16
            if block_idx + 16 > len(block_data):
                continue

            a0 = block_data[block_idx]
            a1 = block_data[block_idx + 1]
            alpha_bits = (struct.unpack_from('<H', block_data, block_idx + 2)[0] |
                          (struct.unpack_from('<I', block_data, block_idx + 4)[0] << 16)) & 0xFFFFFFFFFFFF

            alphas = [a0, a1]
            if a0 > a1:
                for i in range(6):
                    alphas.append(((6 - i) * a0 + (i + 1) * a1) // 7)
            else:
                for i in range(4):
                    alphas.append(((4 - i) * a0 + (i + 1) * a1) // 5)
                alphas.append(0)
                alphas.append(255)

            c0_offset = block_idx + 8
            c0 = struct.unpack_from('<H', block_data, c0_offset)[0]
            c1 = struct.unpack_from('<H', block_data, c0_offset + 2)[0]
            color_bits = struct.unpack_from('<I', block_data, c0_offset + 4)[0]

            r0 = ((c0 >> 11) & 0x1F) * 255 // 31
            g0 = ((c0 >> 5) & 0x3F) * 255 // 63
            b0 = (c0 & 0x1F) * 255 // 31
            r1 = ((c1 >> 11) & 0x1F) * 255 // 31
            g1 = ((c1 >> 5) & 0x3F) * 255 // 63
            b1 = (c1 & 0x1F) * 255 // 31

            colors = [(r0, g0, b0), (r1, g1, b1)]
            colors.append(((2*r0 + r1) // 3, (2*g0 + g1) // 3, (2*b0 + b1) // 3))
            colors.append(((r0 + 2*r1) // 3, (g0 + 2*g1) // 3, (b0 + 2*b1) // 3))

            for i in range(16):
                px = bx + (i % 4)
                py = by + (i // 4)
                if px >= width or py >= height:
                    continue
                idx = (py * width + px) * 4
                alpha_code = (alpha_bits >> (i * 3)) & 7
                color_code = (color_bits >> (i * 2)) & 3
                a = alphas[alpha_code]
                cr, cg, cb = colors[color_code]
                pixels[idx:idx+4] = bytes([cr, cg, cb, a])

    return Image.frombytes('RGBA', (width, height), bytes(pixels))


def read_dds(filepath):
    """读取 DDS 文件（支持 BGRA32 无压缩和 DXT1/DXT5 压缩）"""
    with open(filepath, 'rb') as f:
        header = f.read(128)
        magic = header[:4]
        if magic != b'DDS ':
            raise ValueError('Not a DDS file')

        height = struct.unpack_from('<I', header, 12)[0]
        width = struct.unpack_from('<I', header, 16)[0]
        pitch = struct.unpack_from('<I', header, 20)[0]
        pf_flags = struct.unpack_from('<I', header, 80)[0]
        fourcc = struct.unpack_from('<I', header, 84)[0]
        bpp = struct.unpack_from('<I', header, 88)[0]
        fourcc_str = chr(fourcc & 0xFF) + chr((fourcc >> 8) & 0xFF) + chr((fourcc >> 16) & 0xFF) + chr((fourcc >> 24) & 0xFF)

        f.seek(128)
        # Handle DX10 extended header
        if fourcc == 0x30315844:  # 'DX10'
            f.read(20)  # skip DX10 header
            fourcc_str = 'DXT5'

        if fourcc != 0 and fourcc != 0x30315844:
            # DXT compressed
            if fourcc_str == 'DXT1':
                num_blocks = ((width + 3) // 4) * ((height + 3) // 4)
                block_data = f.read(num_blocks * 8)
                return decode_dxt1(block_data, width, height)
            elif fourcc_str in ('DXT3', 'DXT5'):
                num_blocks = ((width + 3) // 4) * ((height + 3) // 4)
                block_data = f.read(num_blocks * 16)
                return decode_dxt5(block_data, width, height)
            else:
                raise ValueError(f'Unsupported DDS compression: {fourcc_str}')
        elif fourcc == 0x30315844:  # DX10
            num_blocks = ((width + 3) // 4) * ((height + 3) // 4)
            block_data = f.read(num_blocks * 16)
            return decode_dxt5(block_data, width, height)
        else:
            # Uncompressed
            if bpp == 24:
                raw_data = f.read(width * height * 3)
                if len(raw_data) < width * height * 3:
                    raise ValueError(f'Not enough image data: got {len(raw_data)}, expected {width * height * 3}')
                pixels = bytearray(width * height * 4)
                for i in range(width * height):
                    pixels[i*4] = raw_data[i*3]
                    pixels[i*4+1] = raw_data[i*3+1]
                    pixels[i*4+2] = raw_data[i*3+2]
                    pixels[i*4+3] = 255
                return Image.frombytes('RGBA', (width, height), bytes(pixels), 'raw', 'BGRA')
            elif pf_flags == 0x40 and bpp == 16:
                # 16-bit RGB (X1R5G5B5 or R5G6B5)
                r_mask = struct.unpack_from('<I', header, 92)[0]
                g_mask = struct.unpack_from('<I', header, 96)[0]
                b_mask = struct.unpack_from('<I', header, 100)[0]
                raw_data = f.read(width * height * 2)
                if len(raw_data) < width * height * 2:
                    raise ValueError(f'Not enough image data: got {len(raw_data)}, expected {width * height * 2}')
                pixels = bytearray(width * height * 4)
                for i in range(width * height):
                    pixel = struct.unpack_from('<H', raw_data, i * 2)[0]
                    r_bits = r_mask.bit_count()
                    r_shift = (r_mask & -r_mask).bit_length() - 1
                    r_val = ((pixel & r_mask) >> r_shift) * 255 // ((1 << r_bits) - 1) if r_bits > 0 else 0

                    g_bits = g_mask.bit_count()
                    g_shift = (g_mask & -g_mask).bit_length() - 1
                    g_val = ((pixel & g_mask) >> g_shift) * 255 // ((1 << g_bits) - 1) if g_bits > 0 else 0

                    b_bits = b_mask.bit_count()
                    b_shift = (b_mask & -b_mask).bit_length() - 1
                    b_val = ((pixel & b_mask) >> b_shift) * 255 // ((1 << b_bits) - 1) if b_bits > 0 else 0

                    a_val = 255
                    pixels[i*4:i*4+4] = bytes([b_val, g_val, r_val, a_val])  # BGRA order for frombytes
                return Image.frombytes('RGBA', (width, height), bytes(pixels), 'raw', 'BGRA')
            else:
                # 32-bit BGRA uncompressed
                raw_data = f.read(width * height * 4)
                if len(raw_data) < width * height * 4:
                    raise ValueError(f'Not enough image data: got {len(raw_data)}, expected {width * height * 4}')
                return Image.frombytes('RGBA', (width, height), raw_data, 'raw', 'BGRA')


def convert_file(src_path, dst_path):
    """转换单个文件为 PNG"""
    ext = os.path.splitext(src_path)[1].lower()
    try:
        if ext == '.dds':
            with open(src_path, 'rb') as f:
                magic = f.read(4)
            if magic == b'DDS ':
                img = read_dds(src_path)
            else:
                # 非标准格式，让 Pillow 尝试
                img = Image.open(src_path)
                if img.mode in ('P', 'LA', 'PA'):
                    img = img.convert('RGBA')
                elif img.mode == 'L':
                    img = img.convert('RGBA')
        elif ext == '.tga':
            img = Image.open(src_path)
            if img.mode in ('P', 'LA', 'PA'):
                img = img.convert('RGBA')
            elif img.mode == 'L':
                img = img.convert('RGBA')
        else:
            return False
        img.save(dst_path, 'PNG')
        return True
    except Exception as e:
        print(f"  ERROR converting {src_path}: {e}")
        return False


def main():
    src_dir = '/workspace/leaders_icons/leaders'
    out_dir = '/workspace/icons_png'
    os.makedirs(out_dir, exist_ok=True)

    stats = {'total': 0, 'converted': 0, 'failed': 0, 'unknown_country': set()}
    country_stats = defaultdict(lambda: {'total': 0, 'converted': 0})

    for country_code in sorted(os.listdir(src_dir)):
        src_country_path = os.path.join(src_dir, country_code)
        if not os.path.isdir(src_country_path):
            continue

        # 特殊处理 Africa, Europe 等大区域目录
        if country_code in ['Africa', 'Europe', 'joke_bookmark']:
            cn_name = {'Africa': '非洲', 'Europe': '欧洲', 'joke_bookmark': '彩蛋'} \
                .get(country_code, country_code)
        else:
            cn_name = COUNTRY_CN.get(country_code)
            if cn_name is None:
                cn_name = f'未知_{country_code}'
                stats['unknown_country'].add(country_code)

        # 获取所有图片文件
        files = [f for f in os.listdir(src_country_path)
                 if f.lower().endswith(('.dds', '.tga'))]

        if not files:
            continue

        dst_country_path = os.path.join(out_dir, cn_name)
        os.makedirs(dst_country_path, exist_ok=True)

        for filename in files:
            stats['total'] += 1
            country_stats[country_code]['total'] += 1
            src_path = os.path.join(src_country_path, filename)
            # 翻译文件名
            cn_filename = translate_name(filename) + '.png'
            dst_path = os.path.join(dst_country_path, cn_filename)

            if convert_file(src_path, dst_path):
                stats['converted'] += 1
                country_stats[country_code]['converted'] += 1
            else:
                stats['failed'] += 1

        if country_stats[country_code]['converted'] > 0:
            print(f"  [{cn_name}] {country_stats[country_code]['converted']}/{country_stats[country_code]['total']} 个文件已转换")

    # 打印统计
    print(f"\n========== 转换完成 ==========")
    print(f"总计文件: {stats['total']}")
    print(f"成功转换: {stats['converted']}")
    print(f"转换失败: {stats['failed']}")
    print(f"输出目录: {out_dir}")
    if stats['unknown_country']:
        print(f"\n未映射国家代码 ({len(stats['unknown_country'])}): "
              f"{', '.join(sorted(stats['unknown_country']))}")


if __name__ == '__main__':
    main()
