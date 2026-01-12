/**
 * Charts component - Plotly.js wrappers for visualizations.
 */

const Charts = {
    /**
     * Render heatmap for call or put prices
     */
    renderHeatmap(elementId, data, optionType = 'call') {
        const element = document.getElementById(elementId);
        if (!element) {
            console.error(`Element ${elementId} not found`);
            return;
        }

        const prices = optionType === 'call' ? data.call_prices : data.put_prices;
        const title = optionType === 'call' ? 'Call Option Price' : 'Put Option Price';

        // Create trace
        const trace = {
            z: prices,
            x: data.spot_range,
            y: data.vol_range.map(v => (v * 100).toFixed(1)),  // Convert to percentage
            type: 'heatmap',
            colorscale: optionType === 'call' ? 'Blues' : 'Reds',
            hovertemplate: `
                <b>Futures Price:</b> %{x:.2f}<br>
                <b>Volatility:</b> %{y}%<br>
                <b>${title}:</b> %{z:.4f}<br>
                <extra></extra>
            `,
            colorbar: {
                title: 'Price',
                titleside: 'right'
            }
        };

        // Layout configuration
        const layout = {
            xaxis: {
                title: 'Futures Price (KES)',
                tickformat: '.2f'
            },
            yaxis: {
                title: 'Volatility (%)',
                ticksuffix: '%'
            },
            margin: {
                l: 60,
                r: 40,
                t: 30,
                b: 60
            },
            paper_bgcolor: 'rgba(0,0,0,0)',
            plot_bgcolor: 'rgba(0,0,0,0)',
            font: {
                color: this.getTextColor()
            },
            hovermode: 'closest'
        };

        // Config
        const config = {
            responsive: true,
            displayModeBar: false
        };

        Plotly.newPlot(element, [trace], layout, config);

        // Add marker for current values
        if (data.current_spot && data.current_vol) {
            Plotly.addTraces(element, [{
                x: [data.current_spot],
                y: [(data.current_vol * 100).toFixed(1)],
                mode: 'markers',
                marker: {
                    size: 12,
                    color: 'yellow',
                    symbol: 'star',
                    line: {
                        color: 'black',
                        width: 2
                    }
                },
                name: 'Current',
                hovertemplate: `<b>Current Position</b><br>Spot: ${data.current_spot.toFixed(2)}<br>Vol: ${(data.current_vol * 100).toFixed(1)}%<extra></extra>`
            }]);
        }
    },

    /**
     * Render P&L chart
     */
    renderPnLChart(elementId, data, options = {}) {
        const element = document.getElementById(elementId);
        if (!element) {
            console.error(`Element ${elementId} not found`);
            return;
        }

        const traces = [];

        // Total P&L trace
        traces.push({
            x: data.prices,
            y: data.total_pnl,
            type: 'scatter',
            mode: 'lines',
            name: 'Total P&L',
            line: {
                color: 'rgb(31, 119, 180)',
                width: 3
            },
            hovertemplate: `
                <b>Price:</b> %{x:.2f}<br>
                <b>P&L:</b> %{y:.2f}<br>
                <extra></extra>
            `
        });

        // Add individual leg traces if provided
        for (const [key, value] of Object.entries(data)) {
            if (key.startsWith('leg_')) {
                traces.push({
                    x: data.prices,
                    y: value,
                    type: 'scatter',
                    mode: 'lines',
                    name: key.replace(/_/g, ' '),
                    line: {
                        width: 1,
                        dash: 'dot'
                    },
                    hovertemplate: `
                        <b>Price:</b> %{x:.2f}<br>
                        <b>P&L:</b> %{y:.2f}<br>
                        <extra></extra>
                    `
                });
            }
        }

        // Add zero line
        traces.push({
            x: data.prices,
            y: Array(data.prices.length).fill(0),
            type: 'scatter',
            mode: 'lines',
            name: 'Break-even',
            line: {
                color: 'gray',
                width: 1,
                dash: 'dash'
            },
            showlegend: false,
            hoverinfo: 'skip'
        });

        // Layout
        const layout = {
            xaxis: {
                title: 'Underlying Price (KES)',
                tickformat: '.2f'
            },
            yaxis: {
                title: 'Profit/Loss (KES)',
                tickformat: '.2f',
                zeroline: true,
                zerolinecolor: 'gray',
                zerolinewidth: 1
            },
            margin: {
                l: 60,
                r: 40,
                t: 30,
                b: 60
            },
            paper_bgcolor: 'rgba(0,0,0,0)',
            plot_bgcolor: 'rgba(0,0,0,0)',
            font: {
                color: this.getTextColor()
            },
            hovermode: 'x unified',
            showlegend: true,
            legend: {
                x: 1.05,
                y: 1,
                xanchor: 'left',
                yanchor: 'top'
            }
        };

        // Config
        const config = {
            responsive: true,
            displayModeBar: true,
            modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d']
        };

        Plotly.newPlot(element, traces, layout, config);
    },

    /**
     * Render comparison chart (multiple strategies)
     */
    renderComparisonChart(elementId, strategies) {
        const element = document.getElementById(elementId);
        if (!element) {
            console.error(`Element ${elementId} not found`);
            return;
        }

        const colors = [
            'rgb(31, 119, 180)',
            'rgb(255, 127, 14)',
            'rgb(44, 160, 44)',
            'rgb(214, 39, 40)'
        ];

        const traces = strategies.map((strategy, index) => ({
            x: strategy.pnl_data.prices,
            y: strategy.pnl_data.total_pnl,
            type: 'scatter',
            mode: 'lines',
            name: strategy.name,
            line: {
                color: colors[index % colors.length],
                width: 2
            },
            hovertemplate: `
                <b>${strategy.name}</b><br>
                <b>Price:</b> %{x:.2f}<br>
                <b>P&L:</b> %{y:.2f}<br>
                <extra></extra>
            `
        }));

        // Add zero line
        if (strategies.length > 0) {
            traces.push({
                x: strategies[0].pnl_data.prices,
                y: Array(strategies[0].pnl_data.prices.length).fill(0),
                type: 'scatter',
                mode: 'lines',
                name: 'Break-even',
                line: {
                    color: 'gray',
                    width: 1,
                    dash: 'dash'
                },
                showlegend: false,
                hoverinfo: 'skip'
            });
        }

        const layout = {
            xaxis: {
                title: 'Underlying Price (KES)'
            },
            yaxis: {
                title: 'Profit/Loss (KES)',
                zeroline: true,
                zerolinecolor: 'gray'
            },
            margin: {
                l: 60,
                r: 150,
                t: 30,
                b: 60
            },
            paper_bgcolor: 'rgba(0,0,0,0)',
            plot_bgcolor: 'rgba(0,0,0,0)',
            font: {
                color: this.getTextColor()
            },
            hovermode: 'x unified',
            showlegend: true,
            legend: {
                x: 1.05,
                y: 1,
                xanchor: 'left',
                yanchor: 'top'
            }
        };

        const config = {
            responsive: true,
            displayModeBar: true
        };

        Plotly.newPlot(element, traces, layout, config);
    },

    /**
     * Get text color based on current theme
     */
    getTextColor() {
        return document.documentElement.classList.contains('dark') ? '#e5e7eb' : '#1f2937';
    },

    /**
     * Render volatility forecast chart with confidence intervals
     */
    renderVolatilityForecast(elementId, data) {
        const element = document.getElementById(elementId);
        if (!element) {
            console.error(`Element ${elementId} not found`);
            return;
        }

        const traces = [];

        // Actual historical volatility (if provided)
        if (data.historical_dates && data.historical_volatility) {
            traces.push({
                x: data.historical_dates,
                y: data.historical_volatility.map(v => v * 100),
                type: 'scatter',
                mode: 'lines',
                name: 'Historical',
                line: {
                    color: 'rgb(100, 100, 100)',
                    width: 2
                },
                hovertemplate: `
                    <b>Historical</b><br>
                    <b>Date:</b> %{x}<br>
                    <b>Volatility:</b> %{y:.2f}%<br>
                    <extra></extra>
                `
            });
        }

        // Predicted volatility
        if (data.forecast_dates && data.predicted_volatility) {
            traces.push({
                x: data.forecast_dates,
                y: data.predicted_volatility.map(v => v * 100),
                type: 'scatter',
                mode: 'lines+markers',
                name: 'Forecast',
                line: {
                    color: 'rgb(31, 119, 180)',
                    width: 3
                },
                marker: {
                    size: 6
                },
                hovertemplate: `
                    <b>Forecast</b><br>
                    <b>Date:</b> %{x}<br>
                    <b>Volatility:</b> %{y:.2f}%<br>
                    <extra></extra>
                `
            });
        }

        // Upper confidence interval
        if (data.forecast_dates && data.upper_bound) {
            traces.push({
                x: data.forecast_dates,
                y: data.upper_bound.map(v => v * 100),
                type: 'scatter',
                mode: 'lines',
                name: 'Upper 95% CI',
                line: {
                    color: 'rgba(31, 119, 180, 0.3)',
                    width: 1,
                    dash: 'dash'
                },
                fill: 'tonexty',
                fillcolor: 'rgba(31, 119, 180, 0.1)',
                showlegend: true,
                hovertemplate: `
                    <b>Upper CI</b><br>
                    <b>Date:</b> %{x}<br>
                    <b>Volatility:</b> %{y:.2f}%<br>
                    <extra></extra>
                `
            });
        }

        // Lower confidence interval
        if (data.forecast_dates && data.lower_bound) {
            traces.push({
                x: data.forecast_dates,
                y: data.lower_bound.map(v => v * 100),
                type: 'scatter',
                mode: 'lines',
                name: 'Lower 95% CI',
                line: {
                    color: 'rgba(31, 119, 180, 0.3)',
                    width: 1,
                    dash: 'dash'
                },
                showlegend: true,
                hovertemplate: `
                    <b>Lower CI</b><br>
                    <b>Date:</b> %{x}<br>
                    <b>Volatility:</b> %{y:.2f}%<br>
                    <extra></extra>
                `
            });
        }

        const layout = {
            xaxis: {
                title: 'Date',
                type: 'date'
            },
            yaxis: {
                title: 'Volatility (%)',
                ticksuffix: '%'
            },
            margin: {
                l: 60,
                r: 40,
                t: 30,
                b: 60
            },
            paper_bgcolor: 'rgba(0,0,0,0)',
            plot_bgcolor: 'rgba(0,0,0,0)',
            font: {
                color: this.getTextColor()
            },
            hovermode: 'x unified',
            showlegend: true,
            legend: {
                x: 0.02,
                y: 0.98,
                xanchor: 'left',
                yanchor: 'top',
                bgcolor: 'rgba(255,255,255,0.8)'
            }
        };

        const config = {
            responsive: true,
            displayModeBar: true,
            modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d']
        };

        Plotly.newPlot(element, traces, layout, config);
    },

    /**
     * Render backtest chart comparing predicted vs actual
     */
    renderBacktestChart(elementId, data) {
        const element = document.getElementById(elementId);
        if (!element) {
            console.error(`Element ${elementId} not found`);
            return;
        }

        const traces = [];

        // Actual volatility
        if (data.dates && data.actual) {
            traces.push({
                x: data.dates,
                y: data.actual.map(v => v * 100),
                type: 'scatter',
                mode: 'lines+markers',
                name: 'Actual',
                line: {
                    color: 'rgb(44, 160, 44)',
                    width: 2
                },
                marker: {
                    size: 5
                },
                hovertemplate: `
                    <b>Actual</b><br>
                    <b>Date:</b> %{x}<br>
                    <b>Volatility:</b> %{y:.2f}%<br>
                    <extra></extra>
                `
            });
        }

        // Predicted volatility
        if (data.dates && data.predicted) {
            traces.push({
                x: data.dates,
                y: data.predicted.map(v => v * 100),
                type: 'scatter',
                mode: 'lines+markers',
                name: 'Predicted',
                line: {
                    color: 'rgb(31, 119, 180)',
                    width: 2,
                    dash: 'dot'
                },
                marker: {
                    size: 5,
                    symbol: 'square'
                },
                hovertemplate: `
                    <b>Predicted</b><br>
                    <b>Date:</b> %{x}<br>
                    <b>Volatility:</b> %{y:.2f}%<br>
                    <extra></extra>
                `
            });
        }

        const layout = {
            xaxis: {
                title: 'Date',
                type: 'date'
            },
            yaxis: {
                title: 'Volatility (%)',
                ticksuffix: '%'
            },
            margin: {
                l: 60,
                r: 40,
                t: 30,
                b: 60
            },
            paper_bgcolor: 'rgba(0,0,0,0)',
            plot_bgcolor: 'rgba(0,0,0,0)',
            font: {
                color: this.getTextColor()
            },
            hovermode: 'x unified',
            showlegend: true,
            legend: {
                x: 0.02,
                y: 0.98,
                xanchor: 'left',
                yanchor: 'top',
                bgcolor: 'rgba(255,255,255,0.8)'
            }
        };

        const config = {
            responsive: true,
            displayModeBar: true,
            modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d']
        };

        Plotly.newPlot(element, traces, layout, config);
    }
};

// Export for use in other modules
window.Charts = Charts;
