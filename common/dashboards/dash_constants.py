# Plotly chart layout parameter
layout = dict(
    autosize=True,
    automargin=True,
    colorway=['#00007f', '#0000cc', '#0000ff', '#6666ff',
              '#7f7fff', '#9999ff', '#b2b2ff', '#ccccff', '#e5e5ff', '#ebebff'],
    # legend=dict(
    #     orientation="h",
    #     yanchor="top",
    #     # bgcolor="#1f2c56",
    #     # font=dict(color="white"),
    #     x=0,
    #     y=0,
    # ),

    # margin=dict(
    #     l=30,
    #     r=30,
    #     b=20,
    #     t=40
    # ),
    # hovermode="closest",
    # plot_bgcolor="#F9F9F9",
    # paper_bgcolor="#F9F9F9",
    # legend=dict(font=dict(size=10), orientation='h'),
    # title='Satellite Overview',
)

# Plotly chart config parameter
config = dict(
    id='config_id',
    # displayModeBar=False,
    displaylogo=False,
    responsive=True,
    modeBarButtonsToRemove=['pan2d', 'zoomIn2d', 'zoomOut2d',
                            'autoScale2d', 'hoverClosestCartesian', 'hoverCompareCartesian']
)
