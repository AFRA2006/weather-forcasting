import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go

from weather_api import get_weather_by_city
from predict import predict_temperature


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Weather Forecast",
    page_icon="🌤️",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ============================================================
# SESSION STATE
# ============================================================

if "main_section" not in st.session_state:
    st.session_state.main_section = "Current"

if "graph_type" not in st.session_state:
    st.session_state.graph_type = "Temperature"

if "weather_data" not in st.session_state:
    st.session_state.weather_data = None

if "city_name" not in st.session_state:
    st.session_state.city_name = "Islamabad"

if "theme_mode" not in st.session_state:
    st.session_state.theme_mode = "Bright"


# ============================================================
# THEME COLORS
# ============================================================

if st.session_state.theme_mode == "Bright":

    background_color = "#f5f7fb"
    card_color = "#ffffff"
    text_color = "#172033"
    secondary_color = "#667085"
    border_color = "#e5eaf2"
    menu_active_color = "#eaf2ff"

else:

    background_color = "#101827"
    card_color = "#182235"
    text_color = "#ffffff"
    secondary_color = "#aab4c5"
    border_color = "#2d3a50"
    menu_active_color = "#243653"


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    f"""
    <style>

    .stApp {{
        background: {background_color};
        color: {text_color};
    }}

    [data-testid="stHeader"] {{
        background: transparent;
    }}

    [data-testid="stSidebar"] {{
        display: none;
    }}

    .block-container {{
        max-width: 1450px;
        padding-top: 1rem;
        padding-bottom: 1rem;
    }}

    h1, h2, h3, h4, p, label {{
        color: {text_color} !important;
    }}

    .weather-header {{
        background: {card_color};
        border: 1px solid {border_color};
        border-radius: 18px;
        padding: 18px 24px;
        margin-bottom: 14px;
    }}

    .header-title {{
        font-size: 30px;
        font-weight: 750;
        color: {text_color};
        margin-bottom: 3px;
    }}

    .header-subtitle {{
        color: {secondary_color};
        font-size: 14px;
    }}

    .section-box {{
        background: {card_color};
        border: 1px solid {border_color};
        border-radius: 18px;
        padding: 18px;
        margin-bottom: 14px;
    }}

    .section-heading {{
        color: {text_color};
        font-size: 21px;
        font-weight: 700;
        margin-bottom: 4px;
    }}

    .small-text {{
        color: {secondary_color};
        font-size: 13px;
    }}

    .metric-card {{
        background: {card_color};
        border: 1px solid {border_color};
        border-radius: 16px;
        padding: 14px;
        min-height: 105px;
        margin-bottom: 12px;
    }}

    .metric-label {{
        color: {secondary_color};
        font-size: 13px;
        margin-bottom: 8px;
    }}

    .metric-value {{
        color: {text_color};
        font-size: 25px;
        font-weight: 750;
    }}

    .metric-icon {{
        font-size: 23px;
        float: right;
    }}

    .menu-box {{
    background: {card_color};
    border: 1px solid {border_color};
    border-radius: 14px;
    padding: 10px 8px;
    min-height: auto;
    }}

    .menu-title {{
    color: {text_color};
    font-size: 14px;
    font-weight: 700;
    margin-bottom: 8px;
    text-align: center;
    }}
    div.stButton > button {{
    width: 100%;
    min-height: 34px;
    height: 34px;
    border-radius: 8px;
    border: 1px solid {border_color};
    background: {card_color};
    color: {text_color};
    font-size: 12px;
    font-weight: 600;
    text-align: center;
    padding: 2px 5px;
    margin-bottom: 5px;
    line-height: 1;
    }}
    }}

    div.stButton > button:hover {{
        border-color: #3b82f6;
        color: #2563eb;
    }}

    .weather-day-card {{
        background: {card_color};
        border-right: 1px solid {border_color};
        padding: 8px 6px;
        text-align: center;
        min-height: 112px;
    }}

    .weather-day-name {{
        color: {text_color};
        font-size: 14px;
        font-weight: 650;
    }}

    .weather-day-icon {{
        font-size: 28px;
        margin: 5px 0;
    }}

    .weather-day-temp {{
        color: {text_color};
        font-size: 13px;
        font-weight: 650;
    }}

    .weather-day-min {{
        color: {secondary_color};
        font-size: 12px;
    }}

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def metric_card(icon, label, value):
    """
    Displays one weather metric card.
    """

    st.markdown(
        f"""
        <div class="metric-card">
            <span class="metric-icon">{icon}</span>
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def weather_icon(weather_code):
    """
    Converts Open-Meteo weather code into emoji.
    """

    code = int(weather_code)

    if code == 0:
        return "☀️"

    if code in [1, 2, 3]:
        return "🌤️"

    if code in [45, 48]:
        return "🌫️"

    if code in [51, 53, 55, 56, 57]:
        return "🌦️"

    if code in [61, 63, 65, 66, 67]:
        return "🌧️"

    if code in [71, 73, 75, 77]:
        return "❄️"

    if code in [80, 81, 82]:
        return "🌦️"

    if code in [95, 96, 99]:
        return "⛈️"

    return "🌤️"


def get_previous_week_weather(latitude, longitude):
    """
    Gets previous 7 days daily weather data.
    """

    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "past_days": 7,
        "forecast_days": 1,
        "daily": (
            "temperature_2m_max,"
            "temperature_2m_min,"
            "weather_code,"
            "precipitation_sum"
        ),
        "timezone": "auto"
    }

    try:
        response = requests.get(
            url,
            params=params,
            timeout=25
        )

        response.raise_for_status()

        data = response.json()
        daily = data["daily"]

        dataframe = pd.DataFrame({
            "Date": pd.to_datetime(daily["time"]),
            "Max Temperature": daily["temperature_2m_max"],
            "Min Temperature": daily["temperature_2m_min"],
            "Weather Code": daily["weather_code"],
            "Rainfall": daily["precipitation_sum"]
        })

        return dataframe.head(7)

    except Exception as error:
        st.error(f"Previous week weather error: {error}")
        return None


def get_hourly_weather(latitude, longitude):
    """
    Gets next 24 hours weather data.
    """

    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": (
            "temperature_2m,"
            "relative_humidity_2m,"
            "wind_speed_10m,"
            "precipitation"
        ),
        "forecast_days": 2,
        "timezone": "auto"
    }

    try:
        response = requests.get(
            url,
            params=params,
            timeout=25
        )

        response.raise_for_status()

        data = response.json()
        hourly = data["hourly"]

        dataframe = pd.DataFrame({
            "Time": pd.to_datetime(hourly["time"]),
            "Temperature": hourly["temperature_2m"],
            "Humidity": hourly["relative_humidity_2m"],
            "Wind": hourly["wind_speed_10m"],
            "Precipitation": hourly["precipitation"]
        })

        return dataframe.head(24)

    except Exception as error:
        st.error(f"Hourly weather error: {error}")
        return None


def get_weekly_weather(latitude, longitude):
    """
    Gets next 7 days weather forecast.
    """

    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": (
            "temperature_2m_max,"
            "temperature_2m_min,"
            "precipitation_sum,"
            "weather_code"
        ),
        "forecast_days": 7,
        "timezone": "auto"
    }

    try:
        response = requests.get(
            url,
            params=params,
            timeout=25
        )

        response.raise_for_status()

        data = response.json()
        daily = data["daily"]

        dataframe = pd.DataFrame({
            "Date": pd.to_datetime(daily["time"]),
            "Max Temperature": daily["temperature_2m_max"],
            "Min Temperature": daily["temperature_2m_min"],
            "Rainfall": daily["precipitation_sum"],
            "Weather Code": daily["weather_code"]
        })

        return dataframe

    except Exception as error:
        st.error(f"Weekly weather error: {error}")
        return None


def create_temperature_history_graph(dataframe):
    """
    Creates previous-week temperature graph.
    """

    figure = go.Figure()

    figure.add_trace(
        go.Scatter(
            x=dataframe["Date"],
            y=dataframe["Max Temperature"],
            mode="lines+markers+text",
            name="Temperature",
            text=[
                f"{value:.0f}°"
                for value in dataframe["Max Temperature"]
            ],
            textposition="top center",
            line={
                "color": "#f5b400",
                "width": 3,
                "shape": "spline"
            },
            marker={
                "size": 9,
                "color": "#f5b400"
            },
            fill="tozeroy",
            fillcolor="rgba(245, 180, 0, 0.22)",
            hovertemplate=(
                "%{x|%a, %d %b}<br>"
                "Temperature: %{y:.1f}°C"
                "<extra></extra>"
            )
        )
    )

    figure.update_layout(
        height=300,
        margin={
            "l": 10,
            "r": 10,
            "t": 35,
            "b": 10
        },
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={
            "color": text_color
        },
        showlegend=False,
        xaxis={
            "showgrid": False,
            "tickformat": "%a"
        },
        yaxis={
            "showgrid": True,
            "gridcolor": border_color,
            "title": "Temperature °C"
        },
        hovermode="x unified"
    )

    return figure


def create_hourly_graph(dataframe, graph_type):
    """
    Creates selected hourly graph.
    """

    if graph_type == "Temperature":
        column = "Temperature"
        title = "Hourly Temperature"
        y_title = "Temperature °C"
        line_color = "#f5b400"
        fill_color = "rgba(245, 180, 0, 0.20)"

    elif graph_type == "Humidity":
        column = "Humidity"
        title = "Hourly Humidity"
        y_title = "Humidity %"
        line_color = "#0ea5e9"
        fill_color = "rgba(14, 165, 233, 0.20)"

    elif graph_type == "Wind":
        column = "Wind"
        title = "Hourly Wind Speed"
        y_title = "Wind km/h"
        line_color = "#8b5cf6"
        fill_color = "rgba(139, 92, 246, 0.20)"

    else:
        column = "Precipitation"
        title = "Hourly Rainfall"
        y_title = "Rainfall mm"
        line_color = "#2563eb"
        fill_color = "rgba(37, 99, 235, 0.20)"

    figure = go.Figure()

    figure.add_trace(
        go.Scatter(
            x=dataframe["Time"],
            y=dataframe[column],
            mode="lines+markers",
            name=graph_type,
            line={
                "color": line_color,
                "width": 3,
                "shape": "spline"
            },
            marker={
                "size": 6
            },
            fill="tozeroy",
            fillcolor=fill_color,
            hovertemplate=(
                "%{x}<br>"
                + graph_type
                + ": %{y:.2f}"
                + "<extra></extra>"
            )
        )
    )

    figure.update_layout(
        title=title,
        height=340,
        margin={
            "l": 10,
            "r": 10,
            "t": 45,
            "b": 10
        },
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={
            "color": text_color
        },
        showlegend=False,
        xaxis={
            "title": "Time",
            "showgrid": False
        },
        yaxis={
            "title": y_title,
            "showgrid": True,
            "gridcolor": border_color
        },
        hovermode="x unified"
    )

    return figure


# ============================================================
# HEADER
# ============================================================

header_left, header_right = st.columns([6, 0.9])

with header_left:

    st.markdown(
        """
        <div class="weather-header">
            <div class="header-title">
                🌤️ Weather Forecast
            </div>
            <div class="header-subtitle">
                Live weather information for Pakistani cities
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with header_right:

    selected_theme = st.selectbox(
        "Theme",
        ["Bright", "Dim"],
        index=(
            0
            if st.session_state.theme_mode == "Bright"
            else 1
        )
    )

    if selected_theme != st.session_state.theme_mode:
        st.session_state.theme_mode = selected_theme
        st.rerun()


# ============================================================
# CITY SEARCH
# ============================================================

search_col, search_button_col, update_col = st.columns(
    [5, 1.2, 1.2],
    gap="small"
)

with search_col:

    city_input = st.text_input(
        "City Search",
        value=st.session_state.city_name,
        placeholder="Enter city name, e.g. Multan, Lahore, Islamabad",
        label_visibility="collapsed"
    )

with search_button_col:

    search_weather = st.button(
        "🔍 Search Weather",
        use_container_width=True
    )

with update_col:

    update_weather = st.button(
        "🔄 Update Weather",
        use_container_width=True
    )


if search_weather or update_weather:

    if city_input.strip() == "":
        st.warning("Please enter a city name.")

    else:

        with st.spinner("Getting weather information..."):

            result = get_weather_by_city(
                city_input.strip()
            )

        if result:

            st.session_state.weather_data = result
            st.session_state.city_name = city_input.strip()

            st.success(
                f"Weather loaded for {result['city']}"
            )

        else:

            st.error(
                f"City '{city_input}' not found. "
                "Please enter a valid Pakistani city."
            )


# ============================================================
# LOAD DEFAULT WEATHER
# ============================================================

if st.session_state.weather_data is None:

    with st.spinner("Loading Islamabad weather..."):

        default_weather = get_weather_by_city(
            "Islamabad"
        )

    if default_weather:
        st.session_state.weather_data = default_weather


weather = st.session_state.weather_data


# ============================================================
# TOP WEATHER OVERVIEW
# ============================================================

if weather:

    st.markdown(
        f"""
        <div class="section-box">
            <div class="section-heading">
                📍 {weather["city"]} Weather Overview
            </div>
            <div class="small-text">
                Last updated: {weather.get("time", "Current time")}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)

    with metric_col1:
        metric_card(
            "🌡️",
            "Current Temperature",
            f"{weather['temperature']:.1f} °C"
        )

    with metric_col2:
        metric_card(
            "💧",
            "Humidity",
            f"{weather['humidity']:.0f} %"
        )

    with metric_col3:
        metric_card(
            "🌬️",
            "Wind Speed",
            f"{weather['wind_speed']:.1f} km/h"
        )

    with metric_col4:
        metric_card(
            "🌧️",
            "Rainfall",
            f"{weather['rainfall']:.1f} mm"
        )


# ============================================================
# MAIN LAYOUT
# LEFT MENU + RIGHT SELECTED CONTENT
# ============================================================
# ============================================================
# MAIN LAYOUT
# ============================================================

left_menu, main_content = st.columns(
    [0.85, 5.15],
    gap="small"
)


# ============================================================
# LEFT MENU
# ============================================================

with left_menu:

    st.markdown(
        """
        <div class="menu-box">
            <div class="menu-title">MENU</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    if st.button(
        "🌡️ Current",
        use_container_width=True,
        key="menu_current"
    ):
        st.session_state.main_section = "Current"
        st.rerun()

    if st.button(
        "🔮 Prediction",
        use_container_width=True,
        key="menu_prediction"
    ):
        st.session_state.main_section = "Prediction"
        st.rerun()

    if st.button(
        "🕐 Hourly",
        use_container_width=True,
        key="menu_hourly"
    ):
        st.session_state.main_section = "Hourly"
        st.rerun()

    if st.button(
        "📅 Weekly",
        use_container_width=True,
        key="menu_weekly"
    ):
        st.session_state.main_section = "Weekly"
        st.rerun()


# ============================================================
# RIGHT SIDE CONTENT
# ============================================================

with main_content:

    selected_section = st.session_state.main_section


    # ========================================================
    # CURRENT SECTION
    # ========================================================

    if selected_section == "Current":

        st.markdown(
            f"""
            <div class="section-box">
                <div class="section-heading">
                    🌤️ Current Weather Details
                </div>
                <div class="small-text">
                    Live weather information for {weather["city"]}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        current_col1, current_col2 = st.columns(2)

        with current_col1:

            metric_card(
                "🌡️",
                "Current Temperature",
                f"{weather['temperature']:.1f} °C"
            )

            metric_card(
                "💧",
                "Humidity",
                f"{weather['humidity']:.0f} %"
            )

            metric_card(
                "🌬️",
                "Wind Speed",
                f"{weather['wind_speed']:.1f} km/h"
            )

        with current_col2:

            metric_card(
                "🌧️",
                "Rainfall",
                f"{weather['rainfall']:.1f} mm"
            )

            metric_card(
                "🔵",
                "Atmospheric Pressure",
                f"{weather['pressure']:.1f} hPa"
            )

            metric_card(
                "📍",
                "Coordinates",
                (
                    f"{weather['latitude']:.2f}, "
                    f"{weather['longitude']:.2f}"
                )
            )


    # ========================================================
    # PREDICTION SECTION
    # ========================================================

    elif selected_section == "Prediction":

        st.markdown(
            """
            <div class="section-box">
                <div class="section-heading">
                    🔮 Next-Hour Temperature Prediction
                </div>
                <div class="small-text">
                    Predicted temperature from the trained model
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        with st.spinner(
            "Predicting next-hour temperature..."
        ):

            prediction = predict_temperature(
                weather["city"]
            )

        if prediction:

            current_temperature = prediction[
                "current_temperature"
            ]

            predicted_temperature = prediction[
                "predicted_temperature"
            ]

            temperature_change = (
                predicted_temperature
                - current_temperature
            )

            prediction_col1, prediction_col2, prediction_col3 = (
                st.columns(3)
            )

            with prediction_col1:

                metric_card(
                    "🌡️",
                    "Current Temperature",
                    f"{current_temperature:.2f} °C"
                )

            with prediction_col2:

                metric_card(
                    "🔮",
                    "Predicted Next Hour",
                    f"{predicted_temperature:.2f} °C"
                )

            with prediction_col3:

                metric_card(
                    "📈",
                    "Expected Change",
                    f"{temperature_change:+.2f} °C"
                )

        else:

            st.warning(
                "Temperature prediction is not available "
                "for this city."
            )


    # ========================================================
    # HOURLY SECTION
    # ========================================================

    elif selected_section == "Hourly":

        st.markdown(
            """
            <div class="section-box">
                <div class="section-heading">
                    🕐 Hourly Weather
                </div>
                <div class="small-text">
                    Select a graph or view the next 24 hours
                    weather data
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # ----------------------------------------------------
        # HOURLY GRAPH BUTTONS
        # ----------------------------------------------------

        graph_col1, graph_col2, graph_col3, graph_col4 = (
            st.columns(4)
        )

        with graph_col1:

            if st.button(
                "🌡️ Temperature",
                use_container_width=True,
                key="hourly_temperature_button"
            ):
                st.session_state.graph_type = "Temperature"
                st.rerun()

        with graph_col2:

            if st.button(
                "💧 Humidity",
                use_container_width=True,
                key="hourly_humidity_button"
            ):
                st.session_state.graph_type = "Humidity"
                st.rerun()

        with graph_col3:

            if st.button(
                "🌬️ Wind",
                use_container_width=True,
                key="hourly_wind_button"
            ):
                st.session_state.graph_type = "Wind"
                st.rerun()

        with graph_col4:

            if st.button(
                "🌧️ Rainfall",
                use_container_width=True,
                key="hourly_rainfall_button"
            ):
                st.session_state.graph_type = "Precipitation"
                st.rerun()


        # ----------------------------------------------------
        # GET HOURLY DATA
        # ----------------------------------------------------

        hourly_data = get_hourly_weather(
            weather["latitude"],
            weather["longitude"]
        )

        if (
            hourly_data is not None
            and not hourly_data.empty
        ):

            selected_graph = st.session_state.graph_type

            # ------------------------------------------------
            # HOURLY GRAPH
            # ------------------------------------------------

            hourly_graph = create_hourly_graph(
                hourly_data,
                selected_graph
            )

            st.plotly_chart(
                hourly_graph,
                use_container_width=True,
                config={
                    "displayModeBar": False
                }
            )

            # ------------------------------------------------
            # HOURLY TABLE
            # ------------------------------------------------

            st.markdown(
                """
                <div class="section-box">
                    <div class="section-heading">
                        📊 Next 24 Hours Weather
                    </div>
                    <div class="small-text">
                        Hourly temperature, humidity,
                        wind speed and rainfall
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            hourly_table = hourly_data.copy()

            hourly_table["Time"] = hourly_table[
                "Time"
            ].dt.strftime(
                "%d %b, %I:%M %p"
            )

            hourly_table["Temperature"] = hourly_table[
                "Temperature"
            ].map(
                lambda value: f"{value:.1f} °C"
            )

            hourly_table["Humidity"] = hourly_table[
                "Humidity"
            ].map(
                lambda value: f"{value:.0f} %"
            )

            hourly_table["Wind"] = hourly_table[
                "Wind"
            ].map(
                lambda value: f"{value:.1f} km/h"
            )

            hourly_table["Precipitation"] = hourly_table[
                "Precipitation"
            ].map(
                lambda value: f"{value:.1f} mm"
            )

            hourly_table = hourly_table[
                [
                    "Time",
                    "Temperature",
                    "Humidity",
                    "Wind",
                    "Precipitation"
                ]
            ]

            st.dataframe(
                hourly_table,
                use_container_width=True,
                hide_index=True,
                height=300
            )

        else:

            st.warning(
                "Hourly weather data is not available."
            )


    # ========================================================
    # WEEKLY SECTION
    # ========================================================

    elif selected_section == "Weekly":

        st.markdown(
            """
            <div class="section-box">
                <div class="section-heading">
                    📅 Weekly Weather Forecast
                </div>
                <div class="small-text">
                    Upcoming 7 days weather forecast
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        weekly_data = get_weekly_weather(
            weather["latitude"],
            weather["longitude"]
        )

        if (
            weekly_data is not None
            and not weekly_data.empty
        ):

            weekly_table = pd.DataFrame({

                "Day": weekly_data[
                    "Date"
                ].dt.strftime("%A"),

                "Date": weekly_data[
                    "Date"
                ].dt.strftime("%d %b"),

                "Weather": weekly_data[
                    "Weather Code"
                ].apply(weather_icon),

                "Max Temp": (
                    weekly_data["Max Temperature"]
                    .round(1)
                    .astype(str)
                    + " °C"
                ),

                "Min Temp": (
                    weekly_data["Min Temperature"]
                    .round(1)
                    .astype(str)
                    + " °C"
                ),

                "Rainfall": (
                    weekly_data["Rainfall"]
                    .round(1)
                    .astype(str)
                    + " mm"
                )
            })

            st.dataframe(
                weekly_table,
                use_container_width=True,
                hide_index=True,
                height=285,
                column_config={

                    "Day": st.column_config.TextColumn(
                        "Day",
                        width="medium"
                    ),

                    "Date": st.column_config.TextColumn(
                        "Date",
                        width="small"
                    ),

                    "Weather": st.column_config.TextColumn(
                        "Weather",
                        width="small"
                    ),

                    "Max Temp": st.column_config.TextColumn(
                        "Max Temperature",
                        width="medium"
                    ),

                    "Min Temp": st.column_config.TextColumn(
                        "Min Temperature",
                        width="medium"
                    ),

                    "Rainfall": st.column_config.TextColumn(
                        "Rainfall",
                        width="medium"
                    )
                }
            )

        else:

            st.warning(
                "Weekly weather data is not available."
            )