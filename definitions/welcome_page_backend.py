import pandas as pd

import plotly.graph_objects as go

events = pd.read_csv('assets/GenR_timeline.csv', index_col=None)

reporter_colors = {
        'mother': "rgba(33,150,243,0.2)",
        'partner': "rgba(76,175,80,0.2)",
        'child': 'rgba(255,193,7,0.2)',
        'mother-child': 'rgba(255,193,7,0.2)',
        'mother-partner': 'rgba(33,150,243,0.2)', 
        'teacher': 'rgba(0,128,128,0.2)'
    }

period_labels = [
        {"name": "Pregnancy", "start": -0.8, "end": 0},
        {"name": "Perinatal", "start": 0.05, "end": 1},
        {"name": "Preschool", "start": 1.05, "end": 4},
        {"name": "Childhood", "start": 4.05, "end": 11},
        {"name": "Adolescence", "start": 11.05, "end": 18},
        {"name": "Young adulthood", "start": 18.05, "end": 22}
    ]

datatype_to_group = {
    "Blood": "Biological samples & molecular data",
    "Genetics": "Biological samples & molecular data",
    "Urine": "Biological samples & molecular data",
    "Hair": "Biological samples & molecular data",

    "FocusVisit": "General & environmental data",
    "Saliva": "General & environmental data",
    "Record": "General & environmental data",
    "App": "General & environmental data",

    "Ultrasound": "Imaging",

    "Visit": "Physical & clinical measurements",
    "HomeVisit": "Physical & clinical measurements",
    "Actigraphy": "Physical & clinical measurements",

    "Questionnaire": "Questionnaires & interviews",
    "Inteview": "Questionnaires & interviews",
}

def add_background_rectangles(fig, textlabel,  x_start, x_end, y_bottom, y_top, color='rgba(200,200,200,0.2)'):
    # Add a background with periods 
    fig.add_trace(go.Scatter(
        x=[x_start, x_end, x_end, x_start, x_start],
        y=[y_bottom, y_bottom, y_top, y_top, y_bottom],
        fill='toself',
        fillcolor=color,
        line=dict(color='rgba(0,0,0,0)'),
        mode='none',
        showlegend=False,
        hoverinfo='skip'
    ))
    fig.add_trace(go.Scatter(
        x=[(x_start + x_end)/2],
        y=[y_bottom + 0.25],
        text=[textlabel],
        mode='text',
        showlegend=False,
        hoverinfo='skip',
        textfont=dict(family="Arial, sans-serif", size=12, color='rgba(0,0,0,0.5)') #, weight='bold')
    ))

def rounded_rectangle(x0, y0, x1, y1, h):
    # Rounded blobs   
        if (x1 - x0) < 0.05: 
            h = 0.15
        rounded_bottom_left = f' M {x0+h}, {y0} Q {x0}, {y0} {x0}, {y0+h}'
        rounded_top_left = f' L {x0}, {y1-h} Q {x0}, {y1} {x0+h}, {y1}'
        rounded_top_right = f' L {x1-h}, {y1} Q {x1}, {y1} {x1}, {y1-h}'
        rounded_bottom_right = f' L {x1}, {y0+h} Q {x1}, {y0} {x1-h}, {y0}Z'

        return rounded_bottom_left + rounded_top_left+ rounded_top_right + rounded_bottom_right

def assign_y_positions(events):
    row_height = 1.4
    group_spacing = 1.5

    events = events.copy()
    events["data_group"] = events["data_type"].map(datatype_to_group)

    group_order = [
        "Biological samples & molecular data",
        "General & environmental data",
        "Imaging",
        "Physical & clinical measurements",
        "Questionnaires & interviews",
    ]

    event_positions = {}
    category_positions = {}
    current_y = 0

    for group in group_order:

        group_events = (
            events[events["data_group"] == group]
            .sort_values("min_age")
        )

        row_end_times = []

        for event in group_events.itertuples():

            assigned_row = None

            for row_idx, row_end in enumerate(row_end_times):
                if event.min_age >= row_end:
                    assigned_row = row_idx
                    row_end_times[row_idx] = event.max_age
                    break

            if assigned_row is None:
                assigned_row = len(row_end_times)
                row_end_times.append(event.max_age)

            event_positions[event.Index] = (
                current_y - assigned_row * row_height
            )

        group_height = max(len(row_end_times), 1) * row_height

        category_positions[group] = current_y + 0.4

        current_y -= group_height + group_spacing

    events["display_y"] = events.index.map(event_positions)

    y_min = events["display_y"].min() - 1
    y_max = events["display_y"].max() + 1

    return events, y_min, y_max, category_positions, group_order

def make_timeline_agechild(events=events):
    events, y_min, y_max, category_positions, group_order = assign_y_positions(events)
    
    fig = go.Figure()
    fig.update_yaxes(
        range=[y_min, y_max]
    )
    for period in period_labels:
        add_background_rectangles(fig, textlabel = period['name'], x_start=period['start'], x_end=period['end'], y_bottom=y_min + 0.5, y_top=y_max + 0.5)

    label_x = []
    label_y = []
    label_texts = []
    label_customdata = []

    for event in events.itertuples(index=False):
        label_text = event.name
        fig.add_shape(
            type="path",
            path=rounded_rectangle(
                event.min_age,
                event.display_y,
                event.max_age,
                event.display_y + 1.2,
                h=0.15
            ),
            fillcolor=reporter_colors[event.reporter],
            line=dict(width=0)
        )

        label_x.append((event.min_age + event.max_age) / 2)
        label_y.append(event.display_y + 0.6)
        label_texts.append(event.name)

        label_customdata.append(
            [
                event.name,
                event.min_age,
                event.max_age
            ]
        )

    fig.add_trace(
        go.Scatter(
            x=label_x,
            y=label_y,
            text=label_texts,
            customdata=label_customdata,
            textfont=dict(size=9),
            mode="text",
            textposition="middle center",
            showlegend=False,
            hoverinfo="skip",
            name="timeline_labels",
            visible=True
        )
    )



    fig.add_annotation(
        xref="paper", yref="paper",
        x=0.5, y=-0.10,  # position in normalized coordinates below the plot
        showarrow=False,
        text="<b>Age of child (years)</b>",
        font=dict(size=16, color="black", family='Arial'),
        xanchor="center",
    )

    fig.update_layout(
        title="Generation R Timeline",
        xaxis=dict(# title=dict(text="Age of child (years)", 
                   #           font=dict(size=16, family="Arial", color="black", weight="bold"),
                   #           standoff=60),  # distance in pixels to push title away from the axis ticks
                   range=[-1, 23], rangeslider=dict(visible=True)),
        yaxis=dict(range=[y_min - 1, y_max + 1], 
        tickvals=list(category_positions.values()),
        ticktext=[group for group in group_order]),
        plot_bgcolor='white',
        height=600,
        margin=dict(l=20, r=10, t=50, b=50)
    )

    return fig


def make_timeline():
    events = [
        {"name": "GR1001", "start": "2024-01-01", "end": "2024-03-01", "category": "Questionnaire", "level": 1},
        {"name": "GR1002", "start": "2024-03-15", "end": "2024-06-01", "category": "Questionnaire", "level": 1},
        {"name": "Visit0Y", "start": "2024-07-01", "end": "2024-07-10", "category": "Visit", "level": -1},
    ]

    fig = go.Figure()

    # Add duration bars as shapes
    for i, e in enumerate(events):
        fig.add_shape(
            type="rect",
            xref="x",
            yref="y",
            x0=e["start"],
            x1=e["end"],
            y0=e["level"],
            y1=e["level"]+0.5,
            fillcolor="rgba(33,150,243,0.2)",
            line=dict(width=0)
        )
        fig.add_trace(go.Scatter(
            x=[e["start"]],
            y=[e["level"]+0.25],
            text=[f'\t\t{e["name"]}'],
            mode="text",
            textposition="middle right",
            marker=dict(size=20, color="rgb(33,150,243)")
        ))

    fig.update_layout(
        title="Generation R Timeline",
        xaxis=dict(title="Date", type="date", rangeslider=dict(visible=True)),
        # yaxis=dict(
        #     title="Phases",
        #     showgrid=False,
        #     tickvals=list(range(len(events))),
        #     ticktext=[e["category"] for e in events]
        # ),
        height=600,
        margin=dict(l=80, r=30, t=80, b=60)
    )

    return fig