import plotly.graph_objects as go
import plotly.io as pio

pio.templates["document_publishing"] = go.layout.Template(
    layout=go.Layout(
        font=dict(
            family="Calibri, sans-serif",
            size=12,
            color="black"
        ),
        title=dict(
            font=dict(
                family="Calibri, sans-serif",
                size=18,
                color="black"
            )
        ),
        xaxis=dict(
            title=dict(
                font=dict(
                    family="Calibri, sans-serif",
                    size=14,
                    color="black"
                )
            ),
            showline=True,
            zeroline=True,
            zerolinecolor="black",
            zerolinewidth=2,

            showgrid=True,
            gridcolor='grey',
            linecolor='black',
            minor=dict(
                showgrid=True,
                gridcolor='#E5E4E2',
                ticks="inside",
                tickwidth=1,
           )
        ),
        yaxis=dict(
            title=dict(
                font=dict(
                    family="Calibri, sans-serif",
                    size=14,
                    color="black"
                )
            ),
            showline=True,
            zeroline=True,
            zerolinecolor="black",
            zerolinewidth=2,

            showgrid=True,
            gridcolor='grey',
            linecolor='black',
             minor=dict(
                showgrid=True,
                gridcolor='#E5E4E2',
                ticks="inside",
                tickwidth=1,

            )

        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        ),
)

pio.templates.default = "document_publishing"

def main() -> None:
    print("Hello from opus-template!")
