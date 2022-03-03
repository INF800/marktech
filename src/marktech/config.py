class CfgPlot:
    rangebreaks = [
        { 'pattern': 'day of week', 'bounds': [6, 1]},
        { 'pattern': 'hour', 'bounds':[15.5, 9.5]},
        # todo: add holidays (atleast non-moon based)
    ]
    layout_kwds = dict(margin=dict(l=0, r=0, t=0, b=0, pad=0),
                       legend=dict(
                           x=0,
                           y=0.99,
                           traceorder="normal",
                           font=dict(size=12),
                       ),
                       autosize=False,
                       template="plotly_dark",)
    slider_options =  [1000, 2800, 1400]