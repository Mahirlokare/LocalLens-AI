export const API_BASE=(import.meta.env.VITE_API_URL||"https://locallens-ai-api-1sgb.onrender.com/v1").replace(/\/$/,"");
export type Indicator={value:number;source:string;observed_at:string};
export type Neighbourhood={id:string;name:string;city:string;latitude:number|null;longitude:number|null;description:string;indicators:Record<string,Indicator>};
export type Place={display_name:string;latitude:number;longitude:number;category?:string};
export type RouteResult={distance_km:number;duration_minutes:number;mode:string;geometry:string;provider:string;disclaimer:string};
async function request<T>(path:string,init?:RequestInit):Promise<T>{const r=await fetch(API_BASE+path,{...init,headers:{"Content-Type":"application/json",...init?.headers}});if(!r.ok){const b=await r.json().catch(()=>({}));throw new Error(b.detail||`Request failed (${r.status})`)}return r.json() as Promise<T>}
export const api={
 neighbourhoods:(q="")=>request<{items:Neighbourhood[];data_status:string;notice:string}>(`/neighbourhoods${q?`?q=${encodeURIComponent(q)}`:""}`),
 searchPlaces:(q:string)=>request<Place[]>(`/places/search?q=${encodeURIComponent(q)}`),
 suggestPlaces:(q:string)=>request<Place[]>(`/places/suggest?q=${encodeURIComponent(q)}`),
 score:(neighbourhoods:unknown[],weights:Record<string,number>)=>request<{scores:Array<{name:string;score:number;coverage:number;indicators_missing:string[]}>;methodology:string;disclaimer:string}>("/comparisons/score",{method:"POST",body:JSON.stringify({neighbourhoods,weights})}),
 commute:(origin:Place,destination:Place,mode:string)=>request<RouteResult>("/commute/estimate",{method:"POST",body:JSON.stringify({origin_lat:origin.latitude,origin_lon:origin.longitude,destination_lat:destination.latitude,destination_lon:destination.longitude,mode})}),
 aiRecommend:(payload:{question:string;budget_inr?:number;priorities:string[];localities:Array<{name:string;city:string;description:string;indicators:Record<string,Indicator>}>})=>request<{answer:string;model:string;evidence_note:string}>("/ai/recommendations",{method:"POST",body:JSON.stringify(payload)})
};
