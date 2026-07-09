// 全局变量
let stockData = null;
let isHttpMode = false;

// 页面加载完成后初始化
window.addEventListener("DOMContentLoaded", function() {
    checkEnvironment();
});

// 检测运行环境
function checkEnvironment() {
    var isFileProtocol = window.location.protocol === "file:";
    var envBadge = document.getElementById("envBadge");
    var envAlert = document.getElementById("envAlert");

    if (isFileProtocol) {
        envBadge.textContent = "离线模式（无真实数据）";
        envBadge.style.background = "#da3633";
        envAlert.className = "alert alert-error";
        envAlert.innerHTML =
            "❌ <b>当前以文件方式打开，无法加载真实JSON数据</b><br><br>" +
            "<b>解决方案（任选一种）：</b><br>" +
            "① <b>双击运行 <code>start.command</code></b>（推荐，一键启动）<br>" +
            "② 终端执行：<code>cd ~/Desktop/AI quant && python3 -m http.server 8000</code><br>" +
            "   然后在浏览器打开 <code>http://localhost:8000/ma_backtest_local.html</code><br>" +
            "③ 或点击左侧上传CSV数据按钮，手动上传数据文件<br><br>" +
            "<small>提示：不加载数据也可使用模拟数据运行回测（结果仅供参考）</small><br>" +
            "<button class=\"btn btn-secondary\" style=\"margin-top:10px;\" onclick=\"useSimulatedData()\">使用模拟数据</button>";
    } else {
        isHttpMode = true;
        envBadge.textContent = "本地服务器模式（真实数据）";
        envBadge.style.background = "#238636";
        envAlert.className = "alert alert-success";
        envAlert.innerHTML = "✅ 本地服务器已连接，可以加载真实行情数据";
        loadStockData();
    }
}

// 加载股票JSON数据
async function loadStockData() {
    if (!isHttpMode) {
        document.getElementById("dataStatus").innerHTML =
            "<span style=\"color:#f85149;\">⚠️ 请先通过本地服务器或上传CSV加载数据</span>";
        return;
    }

    var tsCode = document.getElementById("stockSelect").value;
    var safeTsCode = tsCode.replace(/\./g, "_");
    var jsonPath = "data/json/" + safeTsCode + ".json";

    try {
        var response = await fetch(jsonPath);
        if (!response.ok) throw new Error("HTTP " + response.status);
        stockData = await response.json();
        showDataInfo(true);
    } catch (e) {
        document.getElementById("dataStatus").innerHTML =
            "<span style=\"color:#f85149;\">❌ JSON加载失败：" + e.message + "<br>请确保 data/json/" + safeTsCode + ".json 文件存在</span>";
    }
}

// 使用模拟数据
function useSimulatedData() {
    var tsCode = document.getElementById("stockSelect").value;
    var nameMap = {
        "300750.SZ": "宁德时代", "601318.SH": "中国平安",
        "600519.SH": "贵州茅台", "601857.SH": "中国石油", "002594.SZ": "比亚迪"
    };
    var startDate = new Date("2024-07-03");
    var dates = [];
    var closes = [];
    var price = 1000;
    for (var i = 0; i < 250; i++) {
        var d = new Date(startDate);
        d.setDate(d.getDate() + i + Math.floor(i / 5) * 2);
        var ds = d.toISOString().slice(0, 10);
        if (dates.indexOf(ds) === -1) {
            dates.push(ds);
            price = Math.max(10, price * (1 + (Math.random() - 0.48) * 0.03));
            closes.push(Math.round(price * 100) / 100);
        }
    }
    var opens = [];
    var highs = [];
    var lows = [];
    var volumes = [];
    for (var j = 0; j < closes.length; j++) {
        opens.push(Math.round(closes[j] * (1 + (Math.random() - 0.5) * 0.005) * 100) / 100);
        highs.push(Math.round(closes[j] * (1 + Math.random() * 0.01) * 100) / 100);
        lows.push(Math.round(closes[j] * (1 - Math.random() * 0.01) * 100) / 100);
        volumes.push(Math.floor(Math.random() * 500000) + 500000);
    }
    stockData = {
        ts_code: tsCode,
        name: nameMap[tsCode] || tsCode,
        dates: dates,
        open: opens,
        high: highs,
        low: lows,
        close: closes,
        volume: volumes
    };
    showDataInfo(false);
    document.getElementById("envAlert").className = "alert alert-warning";
    document.getElementById("envAlert").innerHTML =
        "⚠️ 使用模拟数据运行（非真实行情）<br>如需真实数据，请运行 <code>start.command</code> 启动本地服务器";
}

// 显示数据信息
function showDataInfo(isReal) {
    var dates = stockData.dates;
    var label = isReal
        ? "✅ 真实数据加载成功（" + stockData.name + "）"
        : "⚠️ 使用模拟数据（" + stockData.name + "）";
    document.getElementById("dataStatus").innerHTML =
        label + "<br>数据范围: " + dates[0] + " 至 " + dates[dates.length - 1] + "<br>共 " + dates.length + " 个交易日";
    setDateRange();
}

function setDateRange() {
    var dates = stockData.dates;
    document.getElementById("startDate").value = dates[0];
    document.getElementById("endDate").value = dates[dates.length - 1];
}

// 上传CSV文件
function handleFileUpload(event) {
    var file = event.target.files[0];
    if (!file) return;

    var reader = new FileReader();
    reader.onload = function(e) {
        try {
            var text = e.target.result;
            var lines = text.split("\n");
            var dates = [], opens = [], highs = [], lows = [], closes = [], volumes = [];

            var header = lines[0].split(",");
            var dateIdx = header.findIndex(function(h) { return h.trim() === "trade_date"; });
            var openIdx = header.findIndex(function(h) { return h.trim() === "open"; });
            var highIdx = header.findIndex(function(h) { return h.trim() === "high"; });
            var lowIdx  = header.findIndex(function(h) { return h.trim() === "low"; });
            var closeIdx = header.findIndex(function(h) { return h.trim() === "close"; });
            var volIdx   = header.findIndex(function(h) { return h.trim() === "vol" || h.trim() === "volume"; });

            for (var i = 1; i < lines.length; i++) {
                if (!lines[i].trim()) continue;
                var vals = lines[i].split(",");
                if (vals.length < 6) continue;
                dates.push(vals[dateIdx >= 0 ? dateIdx : 1].trim());
                opens.push(parseFloat(vals[openIdx >= 0 ? openIdx : 2]));
                highs.push(parseFloat(vals[highIdx >= 0 ? highIdx : 3]));
                lows.push(parseFloat(vals[lowIdx >= 0 ? lowIdx : 4]));
                closes.push(parseFloat(vals[closeIdx >= 0 ? closeIdx : 5]));
                volumes.push(parseFloat((volIdx >= 0 ? vals[volIdx] : vals[9]) || 0));
            }

            if (dates.length === 0) throw new Error("CSV解析失败，请检查文件格式");

            stockData = {
                ts_code: file.name.split("_")[0],
                name: file.name.replace(".csv", ""),
                dates: dates,
                open: opens,
                high: highs,
                low: lows,
                close: closes,
                volume: volumes
            };

            document.getElementById("uploadStatus").className = "alert alert-success";
            document.getElementById("uploadStatus").innerHTML = "✅ 文件上传成功: " + file.name + "<br>共 " + dates.length + " 条记录";
            showDataInfo(true);
            document.getElementById("envAlert").className = "alert alert-success";
            document.getElementById("envAlert").innerHTML = "✅ 已加载上传的CSV数据（" + file.name + "）";

        } catch (error) {
            document.getElementById("uploadStatus").className = "alert alert-error";
            document.getElementById("uploadStatus").innerHTML = "❌ 文件解析失败: " + error.message;
        }
    };
    reader.readAsText(file);
}

// 获取参数
function getParams() {
    return {
        ts_code: document.getElementById("stockSelect").value,
        short_window: parseInt(document.getElementById("shortWindow").value),
        long_window:  parseInt(document.getElementById("longWindow").value),
        ma_type: document.getElementById("maType").value,
        trend_filter: document.getElementById("trendFilter").checked,
        atr_filter: document.getElementById("atrFilter").checked,
        initial_capital: parseFloat(document.getElementById("initialCapital").value),
        commission: parseFloat(document.getElementById("commission").value) / 100,
        slippage: parseFloat(document.getElementById("slippage").value) / 100,
        buy_ratio: parseFloat(document.getElementById("buyRatio").value) / 100,
        sell_ratio: parseFloat(document.getElementById("sellRatio").value) / 100,
        start_date: document.getElementById("startDate").value,
        end_date: document.getElementById("endDate").value
    };
}

// 运行回测
function runBacktest() {
    if (!stockData) {
        alert("请先加载股票数据！\n\n方式1：运行 start.command 启动本地服务器\n方式2：点击左侧上传CSV数据按钮");
        return;
    }

    var params = getParams();

    if (params.start_date < stockData.dates[0] || params.end_date > stockData.dates[stockData.dates.length - 1]) {
        alert("日期范围无效！\n可用数据范围：" + stockData.dates[0] + " 至 " + stockData.dates[stockData.dates.length - 1]);
        return;
    }

    document.getElementById("loading").classList.add("active");
    document.getElementById("results").style.display = "none";
    document.getElementById("welcomeMsg").style.display = "none";
    document.getElementById("runBtn").disabled = true;

    setTimeout(function() {
        try {
            var result = executeBacktest(params);
            displayResults(result);
        } catch (error) {
            alert("回测失败：" + error.message);
            console.error(error);
        } finally {
            document.getElementById("loading").classList.remove("active");
            document.getElementById("runBtn").disabled = false;
        }
    }, 100);
}

// 执行回测计算
function executeBacktest(params) {
    var si = stockData.dates.indexOf(params.start_date);
    var ei = stockData.dates.indexOf(params.end_date);
    if (si === -1 || ei === -1 || si > ei) {
        throw new Error("日期范围无效，请检查开始/结束日期");
    }

    var dates  = stockData.dates.slice(si, ei + 1);
    var prices = stockData.close.slice(si, ei + 1);
    var highs  = stockData.high.slice(si, ei + 1);
    var lows   = stockData.low.slice(si, ei + 1);

    // 计算均线（MA 或 EMA）
    var maShort, maLong;
    if (params.ma_type === "EMA") {
        maShort = calcEMA(prices, params.short_window);
        maLong  = calcEMA(prices, params.long_window);
    } else {
        maShort = calcMA(prices, params.short_window);
        maLong  = calcMA(prices, params.long_window);
    }

    // 计算信号（带过滤器）
    var signals = calcSignals(maShort, maLong, prices, highs, lows, params);

    // 执行策略回测
    var strategy = runStrategy(prices, signals, params);

    // 执行BUY-HOLD
    var buyHold = runBuyHold(prices, params);

    // 计算指标
    var metrics = calcMetrics(strategy.nav, buyHold.nav, strategy.trades, params.initial_capital);

    return {
        success: true,
        stock_info: { name: stockData.name, ts_code: params.ts_code },
        metrics: metrics,
        chart_data: { dates: dates, prices: prices, highs: highs, lows: lows, maShort: maShort, maLong: maLong, signals: signals, strategy_nav: strategy.nav, bh_nav: buyHold.nav },
        trades: strategy.trades
    };
}

// 计算MA
function calcMA(prices, window) {
    var ma = [];
    for (var i = 0; i < prices.length; i++) {
        if (i < window - 1) { ma.push(null); continue; }
        var sum = 0;
        for (var j = i - window + 1; j <= i; j++) sum += prices[j];
        ma.push(sum / window);
    }
    return ma;
}

// 计算EMA
function calcEMA(prices, window) {
    var ema = [];
    var k = 2 / (window + 1);
    for (var i = 0; i < prices.length; i++) {
        if (i < window - 1) { ema.push(null); continue; }
        if (i === window - 1) {
            var sum = 0;
            for (var j = 0; j < window; j++) sum += prices[i - j];
            ema.push(sum / window);
        } else {
            ema.push(prices[i] * k + ema[ema.length - 1] * (1 - k));
        }
    }
    return ema;
}

// 计算ATR
function calcATR(highs, lows, prices, window) {
    var tr = [];
    var atr = [];
    for (var i = 0; i < prices.length; i++) {
        if (i === 0) {
            tr.push(highs[i] - lows[i]);
        } else {
            tr.push(Math.max(
                highs[i] - lows[i],
                Math.abs(highs[i] - prices[i-1]),
                Math.abs(lows[i] - prices[i-1])
            ));
        }
        if (i < window - 1) {
            atr.push(null);
        } else if (i === window - 1) {
            var sum = 0;
            for (var j = 0; j < window; j++) sum += tr[i - j];
            atr.push(sum / window);
        } else {
            atr.push((atr[atr.length - 1] * (window - 1) + tr[i]) / window);
        }
    }
    return atr;
}

// 计算信号（带过滤器）
function calcSignals(maShort, maLong, prices, highs, lows, params) {
    var signals = [];
    var maTrend = null;
    var atr = null;
    var atrThreshold = null;

    // 计算趋势过滤器MA
    if (params.trend_filter) {
        maTrend = calcMA(prices, 120);
    }

    // 计算ATR过滤器
    if (params.atr_filter) {
        atr = calcATR(highs, lows, prices, 14);
        // 计算ATR的P20阈值
        var atrValues = atr.filter(function(v) { return v !== null; });
        atrValues.sort(function(a, b) { return a - b; });
        var p20Index = Math.floor(atrValues.length * 0.2);
        atrThreshold = atrValues[p20Index];
    }

    for (var i = 0; i < maShort.length; i++) {
        if (!maShort[i] || !maLong[i] || !maShort[i-1] || !maLong[i-1]) {
            signals.push(0);
            continue;
        }

        var gc = (maShort[i-1] <= maLong[i-1] && maShort[i] > maLong[i]);  // 金叉
        var dc = (maShort[i-1] >= maLong[i-1] && maShort[i] < maLong[i]);  // 死叉

        // 应用趋势过滤器
        if (params.trend_filter && maTrend) {
            if (gc) {
                // 买入信号：价格在MA120上方 且 短MA在MA120上方
                if (!(prices[i] > maTrend[i] && maShort[i] > maTrend[i])) {
                    gc = false;
                }
            }
            if (dc) {
                // 卖出信号：价格在MA120下方 且 短MA在MA120下方
                if (!(prices[i] < maTrend[i] && maShort[i] < maTrend[i])) {
                    dc = false;
                }
            }
        }

        // 应用ATR过滤器
        if (params.atr_filter && atr && atrThreshold !== null) {
            if (gc || dc) {
                // 只有ATR高于P20时才交易
                if (atr[i] === null || atr[i] < atrThreshold) {
                    gc = false;
                    dc = false;
                }
            }
        }

        if (gc) {
            signals.push(1);
        } else if (dc) {
            signals.push(-1);
        } else {
            signals.push(0);
        }
    }
    return signals;
}

// 执行策略回测
function runStrategy(prices, signals, params) {
    var cash = params.initial_capital;
    var shares = 0;
    var nav = [cash];
    var trades = [];

    for (var i = 1; i < prices.length; i++) {
        if (signals[i] === 1 && shares === 0) {
            var buyPrice = prices[i] * (1 + params.slippage);
            var toBuy = Math.floor(cash * params.buy_ratio / buyPrice / (1 + params.commission));
            if (toBuy > 0) {
                cash -= toBuy * buyPrice * (1 + params.commission);
                shares += toBuy;
                trades.push({ type: "BUY", price: buyPrice, shares: toBuy, date: i });
            }
        } else if (signals[i] === -1 && shares > 0) {
            var sellPrice = prices[i] * (1 - params.slippage);
            var toSell = Math.floor(shares * params.sell_ratio);
            if (toSell > 0) {
                cash += toSell * sellPrice * (1 - params.commission);
                shares -= toSell;
                trades.push({ type: "SELL", price: sellPrice, shares: toSell, date: i });
            }
        }
        nav.push(cash + shares * prices[i]);
    }
    return { nav: nav, trades: trades };
}

// 执行BUY-HOLD
function runBuyHold(prices, params) {
    var buyPrice = prices[0] * (1 + params.slippage);
    var shares = Math.floor(params.initial_capital / buyPrice / (1 + params.commission));
    var cash = params.initial_capital - shares * buyPrice * (1 + params.commission);
    var nav = prices.map(function(p) { return cash + shares * p; });
    return { nav: nav };
}

// 计算指标
function calcMetrics(strategyNav, bhNav, trades, initial) {
    var sr = (strategyNav[strategyNav.length - 1] - initial) / initial;
    var br = (bhNav[bhNav.length - 1] - initial) / initial;

    var strReturns = [];
    for (var i = 1; i < strategyNav.length; i++) {
        strReturns.push((strategyNav[i] - strategyNav[i-1]) / strategyNav[i-1]);
    }
    var meanRet = strReturns.reduce(function(a, b) { return a + b; }, 0) / strReturns.length;
    var stdRet  = Math.sqrt(strReturns.reduce(function(a, b) { return a + Math.pow(b - meanRet, 2); }, 0) / strReturns.length);
    var sharpe = stdRet === 0 ? 0 : (meanRet / stdRet) * Math.sqrt(252);

    var maxNav = strategyNav[0], maxDD = 0;
    for (var j = 1; j < strategyNav.length; j++) {
        if (strategyNav[j] > maxNav) maxNav = strategyNav[j];
        var dd = (strategyNav[j] - maxNav) / maxNav;
        if (dd < maxDD) maxDD = dd;
    }

    var win = 0, totalSell = 0;
    for (var k = 0; k < trades.length; k++) {
        if (trades[k].type === "SELL" && k > 0 && trades[k-1].type === "BUY") {
            totalSell++;
            if (trades[k].price > trades[k-1].price) win++;
        }
    }

    return {
        strategy_total_return: sr,
        bh_total_return: br,
        excess_return: sr - br,
        sharpe: sharpe,
        max_drawdown: maxDD,
        num_trades: trades.length,
        win_rate: totalSell === 0 ? 0 : win / totalSell
    };
}

// 显示结果
function displayResults(result) {
    document.getElementById("results").style.display = "block";
    document.getElementById("statusMessage").innerHTML =
        "✅ 回测完成！" + result.stock_info.name + "（" + result.stock_info.ts_code + "）";
    displayMetrics(result.metrics);
    drawCharts(result.chart_data, result.trades, result.chart_data.dates);
    displayTrades(result.trades, result.chart_data.dates);
}

// 显示指标卡片
function displayMetrics(m) {
    var g = document.getElementById("metricsGrid");
    var sr = (m.strategy_total_return * 100).toFixed(2);
    var br = (m.bh_total_return * 100).toFixed(2);
    var er = (m.excess_return * 100).toFixed(2);
    var wr = (m.win_rate * 100).toFixed(1);
    g.innerHTML =
        "<div class=\"metric-card\">" +
            "<div class=\"metric-label\">策略收益率</div>" +
            "<div class=\"metric-value " + (sr >= 0 ? "positive" : "negative") + "\">" + sr + "%</div>" +
        "</div>" +
        "<div class=\"metric-card\">" +
            "<div class=\"metric-label\">BUY-HOLD收益率</div>" +
            "<div class=\"metric-value " + (br >= 0 ? "positive" : "negative") + "\">" + br + "%</div>" +
        "</div>" +
        "<div class=\"metric-card\">" +
            "<div class=\"metric-label\">超额收益</div>" +
            "<div class=\"metric-value " + (er >= 0 ? "positive" : "negative") + "\">" + er + "%</div>" +
        "</div>" +
        "<div class=\"metric-card\">" +
            "<div class=\"metric-label\">夏普比率</div>" +
            "<div class=\"metric-value\">" + m.sharpe.toFixed(2) + "</div>" +
        "</div>" +
        "<div class=\"metric-card\">" +
            "<div class=\"metric-label\">最大回撤</div>" +
            "<div class=\"metric-value negative\">" + (m.max_drawdown * 100).toFixed(2) + "%</div>" +
        "</div>" +
        "<div class=\"metric-card\">" +
            "<div class=\"metric-label\">交易次数 / 胜率</div>" +
            "<div class=\"metric-value\">" + m.num_trades + " / " + wr + "%</div>" +
        "</div>";
}

// 绘制图表
function drawCharts(data, trades, dates) {
    var t1 = { x: dates, y: data.prices, type: "line", name: "股价", line: { color: "#388bfd" } };
    var t2 = { x: dates, y: data.maShort, type: "line", name: "短均线(" + document.getElementById("shortWindow").value + ")", line: { color: "orange", width: 1 } };
    var t3 = { x: dates, y: data.maLong,  type: "line", name: "长均线(" + document.getElementById("longWindow").value + ")", line: { color: "cyan", width: 1 } };

    var buyX = [], buyY = [], sellX = [], sellY = [];
    trades.forEach(function(t) {
        var d = dates[t.date];
        if (t.type === "BUY")  { buyX.push(d);  buyY.push(t.price); }
        if (t.type === "SELL") { sellX.push(d); sellY.push(t.price); }
    });

    var t4 = { x: buyX, y: buyY, mode: "markers", name: "买入", marker: { symbol: "triangle-up", size: 12, color: "#3fb950" } };
    var t5 = { x: sellX, y: sellY, mode: "markers", name: "卖出", marker: { symbol: "triangle-down", size: 12, color: "#f85149" } };

    Plotly.newPlot("priceChart", [t1,t2,t3,t4,t5], {
        title: "股价走势 & 交易信号",
        xaxis: { title: "日期" },
        yaxis: { title: "价格（元）" },
        hovermode: "closest"
    });

    var t6 = { x: dates, y: data.strategy_nav, type: "line", name: "策略净值", line: { color: "#388bfd" } };
    var t7 = { x: dates, y: data.bh_nav,       type: "line", name: "BUY-HOLD", line: { color: "#8b949e", dash: "dash" } };
    Plotly.newPlot("navChart", [t6, t7], {
        title: "策略净值 vs BUY-HOLD",
        xaxis: { title: "日期" },
        yaxis: { title: "净值（元）" }
    });
}

// 显示交易记录表
function displayTrades(trades, dates) {
    if (!trades || trades.length === 0) {
        document.getElementById("tradesTable").innerHTML =
            "<p style=\"color:#8b949e; text-align:center; padding:20px;\">暂无交易记录</p>";
        return;
    }
    var html = "<table class=\"trades-table\"><tr><th>序号</th><th>操作</th><th>日期</th><th>价格</th><th>数量</th></tr>";
    trades.forEach(function(t, i) {
        var action = t.type === "BUY" ? "买入" : "卖出";
        var color  = t.type === "BUY" ? "color:#3fb950;" : "color:#f85149;";
        var dateStr = dates[t.date] || "N/A";
        html += "<tr>" +
            "<td>" + (i+1) + "</td>" +
            "<td style=\"" + color + "\">" + action + "</td>" +
            "<td>" + dateStr + "</td>" +
            "<td>" + t.price.toFixed(2) + "</td>" +
            "<td>" + t.shares + "</td>" +
        "</tr>";
    });
    html += "</table>";
    document.getElementById("tradesTable").innerHTML = html;
}

// 重置参数
function resetParams() {
    document.getElementById("shortWindow").value = 5;
    document.getElementById("longWindow").value  = 15;
    document.getElementById("maType").value = "MA";
    document.getElementById("trendFilter").checked = true;
    document.getElementById("atrFilter").checked = true;
    document.getElementById("initialCapital").value = 100000;
    document.getElementById("commission").value = 0.03;
    document.getElementById("slippage").value  = 0.01;
    document.getElementById("buyRatio").value  = 100;
    document.getElementById("sellRatio").value = 100;
    if (stockData) {
        document.getElementById("startDate").value = stockData.dates[0];
        document.getElementById("endDate").value  = stockData.dates[stockData.dates.length - 1];
    }
    alert("参数已重置为默认值");
}
