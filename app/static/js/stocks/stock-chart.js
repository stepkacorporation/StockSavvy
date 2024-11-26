anychart.onDocumentReady(function () {
    anychart.format.inputLocale('en-us');
    anychart.format.outputLocale('ru-ru');

    const BASE_URL = "http://127.0.0.1:8000/";
    const STOCK_URL = `${BASE_URL}api/stocks/${stockTicker}/`;
    const STOCK_CANDLES_URL = `${STOCK_URL}candles/?all=true`;

    let data;
    let firstLoad = true;
    let emaSeries;
    const table = anychart.data.table();

    const loadData = (url) => {
        axios.get(url)
            .then(response => {
                document.querySelector('#stock-chart #chart-spinner').classList.add('hidden');

                data = response.data;
                const results = data.results.map(item => [
                    item.end_time,
                    parseFloat(item.open),
                    parseFloat(item.high),
                    parseFloat(item.low),
                    parseFloat(item.close),
                    parseFloat(item.value),
                    parseFloat(item.volume),
                ]);
                table.addData(results);
                drawChart('candlestick');

                document.getElementById("chart-controls").classList.remove("hidden");
            })
            .catch(error => {
                console.error('Error fetching data:', error)
                document.querySelector('#stock-chart #chart-spinner').classList.add('hidden');
                document.querySelector('#stock-chart #no-data').style.display = 'block';
            });
    };

    const chart = anychart.stock();
    const title = chart.title();
    title.enabled(true);
    title.useHtml(true);
    title.align("right");
    title.fontSize(12);

    // Функция для динамического изменения размера шрифта
    function updateTitleFontSize() {
        const screenWidth = window.innerWidth;
        let fontSize;

        if (screenWidth <= 480) {
            fontSize = 10;
        } else {
            fontSize = 12;
        }

        title.fontSize(fontSize);
    }


    updateTitleFontSize();

    // Добавить слушатель события изменения размера окна
    window.addEventListener('resize', updateTitleFontSize);

    const plot = chart.plot(0);
    plot.legend().enabled(false);
    // Настройка сетки для оси Y
    plot.yMinorGrid().stroke("oklch(var(--b3))");
    // Настройка сетки для оси X
    plot.xMinorGrid().stroke("oklch(var(--b3))");
    // Настройка меток значений (labels) на оси Y
    plot.yAxis().labels().fontColor("oklch(var(--bc))")   // Цвет шрифта
    // Настройка "тик" (маленьких линий) на оси Y
    plot.yAxis().ticks().stroke("oklch(var(--bc))", 1) // Цвет и толщина "тик"
    // Настройка основной линии оси Y (если нужна)
    plot.yAxis().stroke("oklch(var(--bc))", 1); // Цвет и толщина линии

    chart.container('stock-chart');
    chart.background({fill: "oklch(var(--b1))"});

    // Настройка цвета таймлайна
    chart.scroller()
        .fill("oklch(var(--b3))")          // Задний фон таймлайна
        .selectedFill("oklch(var(--b2))")     // Цвет выделенной области
        .outlineStroke("oklch(var(--pc))", 1)
        .xAxis(false);  // Настройка цвета сетки на оси X в скроллере

    // Настройка графика внутри таймлайна
    const scrollerSeries = chart.scroller().area(table);
    scrollerSeries.fill("oklch(var(--bc))", 0.3);           // Цвет заливки для всего графика
    scrollerSeries.stroke("oklch(var(--bc))", 0.5)            // Цвет линии для всего графика
    scrollerSeries.selected().fill("oklch(var(--in)", 0.3);
    scrollerSeries.selected().stroke("oklch(var(--in)", 1);

    chart.scroller().thumbs().fill('oklch(var(--pc))');

//    let rangePicker = anychart.ui.rangePicker();
//    const rangePickerContainer = document.getElementById("rangePickerContainer");
//    rangePicker.format('dd.MM.yyyy');
//    rangePicker.target(chart)
//    rangePicker.render(rangePickerContainer);
//
//    let rangeSelector = anychart.ui.rangeSelector();
//    let customRanges = rangeSelector.ranges();
//    customRanges[0].count = 7;
//    customRanges[0].text = "7D";
//    rangeSelector.ranges(customRanges);
//    rangeSelector.target(chart)
//    const rangeSelectorContainer = document.getElementById("rangeSelectorContainer");
//    rangeSelector.render(rangeSelectorContainer);
//
//    rangeSelectorContainer.addEventListener("click", function (e) {
//        const selectedRange = chart.getSelectedRange();
//        console.log(selectedRange.firstSelected, selectedRange.lastSelected)
//        calculateAndDrawPriceChange(selectedRange.firstSelected, selectedRange.lastSelected);
//    });

    const seriesMapping = {};

    const drawChart = (chartType) => {
        plot.removeAllSeries();

        createEMA();

        if (chartType === "candlestick") {
            seriesMapping['main'] = table.mapAs({
                'x': 0,
                'open': 1,
                'high': 2,
                'low': 3,
                'close': 4,
                'value': 5,
                'volume': 6,
            });
            const series = plot.candlestick(seriesMapping['main']);
            series.tooltip().format('Open: {%open}\nHigh: {%high}\nLow: {%low}\nClose: {%close}\nValue: {%value}\nVolume: {%volume}');

            // Настройка цветов для нисходящих и восходящих свечей
            series.fallingFill("oklch(var(--er))");    // Цвет заливки для нисходящих свечей
            series.fallingStroke("oklch(var(--er))", 1); // Цвет и толщина линии для нисходящих свечей

            series.risingFill("oklch(var(--su))");    // Цвет заливки для восходящих свечей
            series.risingStroke("oklch(var(--su))", 1); // Цвет и толщина линии для восходящих свечей
        } else if (chartType === "ohlc") {
            seriesMapping['main'] = table.mapAs({
                'x': 0,
                'open': 1,
                'high': 2,
                'low': 3,
                'close': 4,
                'value': 5,
                'volume': 6,
            });
            const series = plot.ohlc(seriesMapping['main']);
            series.tooltip().format('Open: {%open}\nHigh: {%high}\nLow: {%low}\nClose: {%close}\nValue: {%value}\nVolume: {%volume}');

            // Настройка цветов для нисходящих и восходящих свечей
            series.fallingFill("oklch(var(--er))");    // Цвет заливки для нисходящих свечей
            series.fallingStroke("oklch(var(--er))", 1); // Цвет и толщина линии для нисходящих свечей

            series.risingFill("oklch(var(--su))");    // Цвет заливки для восходящих свечей
            series.risingStroke("oklch(var(--su))", 1); // Цвет и толщина линии для восходящих свечей
        } else if (chartType === "line") {
            seriesMapping['main'] = table.mapAs({ 'x': 0, 'value': 4 });
            const series = plot.line(seriesMapping['main']);
            series.tooltip().format('Цена: {%value}');
            series.stroke("oklch(var(--p))", 2);
        } else if (chartType === "area") {
            seriesMapping['main'] = table.mapAs({ 'x': 0, 'value': 4 });
            const series = plot.area(seriesMapping['main']);
            series.tooltip().format('Цена: {%value}');
            series.stroke("oklch(var(--p))", 2);
            series.fill("oklch(var(--p))", 0.5);
        } else if (chartType === "stepArea") {
            seriesMapping['main'] = table.mapAs({ 'x': 0, 'value': 4 });
            const series = plot.stepArea(seriesMapping['main']);
            series.tooltip().format('Цена: {%value}');
            series.stroke("oklch(var(--p))", 2);
            series.fill("oklch(var(--p))", 0.5);
        } else if (chartType === "stepLine") {
            seriesMapping['main'] = table.mapAs({ 'x': 0, 'value': 4 });
            const series = plot.stepLine(seriesMapping['main']);
            series.tooltip().format('Цена: {%value}');
            series.stroke("oklch(var(--p))", 2);
        } else if (chartType === 'stick') {
            seriesMapping['main'] = table.mapAs({ 'x': 0, 'value': 4 });
            const series = plot.stick(seriesMapping['main']);
            series.tooltip().format('Цена: {%value}');
            series.stroke("oklch(var(--p))", 2);
        } else if (chartType === "rangeSplineArea") {
            seriesMapping['main'] = table.mapAs({ 'x': 0, 'high': 2, 'low': 3 });
            const series = plot.rangeSplineArea(seriesMapping['main']);
            series.tooltip().format('High: {%high}\nLow: {%low}');
            series.fill("oklch(var(--p))", 0.5);
            series.highStroke("oklch(var(--p))", 1.5);
            series.lowStroke("oklch(var(--p))", 1.5);
        } else if (chartType === "hilo") {
            seriesMapping['main'] = table.mapAs({ 'x': 0, 'high': 2, 'low': 3 });
            const series = plot.hilo(seriesMapping['main']);
            series.tooltip().format('High: {%high}\nLow: {%low}');
            series.stroke("oklch(var(--p))", 2);
        }

        if (firstLoad) {
            firstLoad = false;
            const end_date = new Date(data.results[0].end_time);
            const start_date = new Date(end_date.getTime() - (365 * 24 * 60 * 60 * 1000));
            chart.selectRange(start_date, end_date);
            calculateAndDrawPriceChange(start_date, end_date);
        }

        chart.draw();
    };

    loadData(STOCK_CANDLES_URL);

    // SELECT CHART TYPE
    document.getElementById("chart-type").addEventListener('change', function () {
        const selectedChartType = this.value;
        drawChart(selectedChartType);
    });

    // ZOOM SETTINGS
    const chartContainer = document.getElementById('stock-chart');

    const xScale = chart.xScale();
    let min = null;
    let max = null;
    let gap = null;

    let wheelTimer;

    chartContainer.addEventListener('wheel', function (event) {
        event.preventDefault();

        const delta = Math.sign(event.deltaY);
        const mouseX = event.offsetX / chartContainer.offsetWidth;

        max = xScale.getMaximum();
        min = xScale.getMinimum();
        gap = max - min;

        let newMin;
        let newMax;

        if (delta > 0) {
            newMin = min - gap * 0.1 * mouseX;
            newMax = max + gap * 0.1 * (1 - mouseX);

            chart.selectRange(newMin, newMax);

            if (newMax > max) {
                newMax = max;
            }
            if (newMin < min) {
                newMin = min;
            }
//            updateRangePicker(newMin, newMax);
        } else if (delta < 0) {
            newMin = min + gap * 0.1 * mouseX;
            newMax = max - gap * 0.1 * (1 - mouseX);
            const newGap = newMax - newMin;

            if (newGap > 2 * 24 * 60 * 60 * 1000) {
                chart.selectRange(newMin, newMax);
//                updateRangePicker(newMin, newMax)
            }
        }

        clearTimeout(wheelTimer);
        wheelTimer = setTimeout(() => {
            calculateAndDrawPriceChange(newMin, newMax);
        }, 350);
    });

//    const updateRangePicker = (min, max) => {
//        const rangePickerInputFields = rangePickerContainer.querySelectorAll("input.anychart-label-input");
//
//        rangePickerInputFields[0].value = formatDate(new Date(min));
//        rangePickerInputFields[1].value = formatDate(new Date(max));
//    };

    const formatDate = (date) => {
        const day = String(date.getDate()).padStart(2, '0');
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const year = date.getFullYear();
        return `${day}.${month}.${year}`;
    }

    // EMA SETTINGS
    const createEMA = () => {
        const emaSwitch = document.getElementById('emaSwitch');
        seriesMapping['ema'] = table.mapAs({ 'x': 0, 'value': 4 });
        emaSeries = plot.ema(seriesMapping['ema']).series().stroke('1.5 oklch(var(--in))');

        if (emaSwitch.checked) {
            emaSeries.enabled(true);
        } else {
            emaSeries.enabled(false);
        }

        emaSwitch.addEventListener('change', function () {
            if (this.checked) {
                emaSeries.enabled(true);
            } else {
                emaSeries.enabled(false);
            }
        });
    };

    chart.listen("selectedrangechangefinish", function (e) {
        calculateAndDrawPriceChange(e.firstSelected, e.lastSelected);
    });


    const calculateAndDrawPriceChange = (startDateTime, endDateTime) => {
        const getCandleDataInDate = (dateTime) => {
            let minDiff = Number.MAX_SAFE_INTEGER;
            let closestIndex = -1;

            for (let i = 0; i < data.results.length; i++) {
                const item = data.results[i];
                const itemDate = new Date(item.start_time);
                const diff = Math.abs(dateTime - itemDate);

                if (diff < minDiff) {
                    minDiff = diff;
                    closestIndex = i;
                }
            }

            if (closestIndex !== -1) {
                return data.results[closestIndex];
            }
        };

        const firstPrice = getCandleDataInDate(new Date(startDateTime)).open;
        const lastPrice = getCandleDataInDate(new Date(endDateTime)).close;

        const priceChange = lastPrice - firstPrice;
        const percentChange = (priceChange / firstPrice) * 100;

        const formattedPriceChange = priceChange.toFixed(decimals);
        const formattedPercentChange = percentChange.toFixed(2);

        const priceChangeText = priceChange > 0 ? `+${formattedPriceChange}` : formattedPriceChange;
        const percentageChangeText = `(${Math.abs(formattedPercentChange)}%)`;

        let priceChangeTitleText = `${priceChangeText} ${percentageChangeText}`;
        if (priceChange > 0) {
            priceChangeTitleText = "<span style=\"color: oklch(var(--su));\">" + priceChangeTitleText + "</span>";
        } else if (priceChange < 0) {
            priceChangeTitleText = "<span style=\"color: oklch(var(--er));\">" + priceChangeTitleText + "</span>";
        }
        title.text(priceChangeTitleText);
    };
});