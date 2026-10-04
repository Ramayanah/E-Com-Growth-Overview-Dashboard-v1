"""Reusable Plotly charts for the E-Commerce Growth Overview dashboard."""

import plotly.graph_objects as go

import config


def revenue_trend_chart(analysis):
    """Return a revenue line chart at the selected time granularity."""
    periods = analysis["series"]
    figure = go.Figure(
        go.Scatter(
            x=periods.index,
            y=periods["revenue"],
            mode="lines+markers",
            name="Revenue",
            line={"color": config.CHART_COLORS[0], "width": 3},
            marker={"size": 6},
            hovertemplate="%{x|%b %d, %Y}<br>Revenue: ₹%{y:,.2f}<extra></extra>",
        )
    )
    return _style_figure(figure, "Revenue Trend", "Revenue (₹)")


def orders_trend_chart(analysis):
    """Return an orders line chart at the selected time granularity."""
    periods = analysis["series"]
    figure = go.Figure(
        go.Scatter(
            x=periods.index,
            y=periods["orders"],
            mode="lines+markers",
            name="Orders",
            line={"color": config.CHART_COLORS[1], "width": 3},
            marker={"size": 6},
            hovertemplate="%{x|%b %d, %Y}<br>Orders: %{y:,.0f}<extra></extra>",
        )
    )
    return _style_figure(figure, "Orders Trend", "Orders")


def revenue_vs_orders_chart(analysis):
    """Compare indexed revenue and orders, both rebased to their first positive value."""
    periods = analysis["series"]
    figure = go.Figure()
    for metric, name, color in (
        ("revenue", "Revenue", config.CHART_COLORS[0]),
        ("orders", "Orders", config.CHART_COLORS[1]),
    ):
        values = periods[metric].astype(float)
        positive_values = values[values > 0]
        indexed = (
            values / positive_values.iloc[0] * 100
            if not positive_values.empty
            else values.where(False)
        )
        figure.add_trace(
            go.Scatter(
                x=periods.index,
                y=indexed,
                mode="lines+markers",
                name=name,
                line={"color": color, "width": 3},
                marker={"size": 5},
                hovertemplate="%{x|%b %d, %Y}<br>%{y:.1f}<extra></extra>",
            )
        )
    return _style_figure(figure, "Revenue vs Orders (Indexed)", "Index (first positive period = 100)")


def aov_trend_chart(analysis):
    """Return an average-order-value line chart at the selected granularity."""
    periods = analysis["series"]
    figure = go.Figure(
        go.Scatter(
            x=periods.index,
            y=periods["aov"],
            mode="lines+markers",
            name="AOV",
            line={"color": config.CHART_COLORS[2], "width": 3},
            marker={"size": 6},
            connectgaps=False,
            hovertemplate="%{x|%b %d, %Y}<br>AOV: ₹%{y:,.2f}<extra></extra>",
        )
    )
    return _style_figure(figure, "Average Order Value Trend", "AOV (₹)")


def _style_figure(figure, title, y_axis_title):
    figure.update_layout(
        title={"text": title, "x": 0.02, "xanchor": "left"},
        template=config.CHART_TEMPLATE,
        height=config.CHART_HEIGHT,
        margin={"l": 12, "r": 12, "t": 54, "b": 12},
        hovermode="x unified",
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.02, "x": 1, "xanchor": "right"},
        xaxis_title="Period",
        yaxis_title=y_axis_title,
    )
    return figure
