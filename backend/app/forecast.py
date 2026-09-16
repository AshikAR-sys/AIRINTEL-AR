from datetime import timedelta

def moving_average_forecast(points,horizon=7):
    if not points: return []
    values=[float(v) for _,v in points]
    window=min(7,len(values))
    level=sum(values[-window:])/window
    recent=values[-min(3,len(values)):]
    slope=(recent[-1]-recent[0])/(len(recent)-1) if len(recent)>1 else 0.0
    last=points[-1][0]
    return [(last+timedelta(days=i),round(max(0,level+slope*i),2)) for i in range(1,horizon+1)]
