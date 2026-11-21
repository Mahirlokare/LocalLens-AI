import {useMemo,useState} from "react";
import {Sparkles,Send,Info} from "lucide-react";
import {api,type Neighbourhood} from "./api";

const priorityOptions=["Affordable housing","Public transport","Healthcare","Education","Environment","Short commute","Family-friendly facilities"];

export default function AIAdvisor({areas}:{areas:Neighbourhood[]}){
 const [question,setQuestion]=useState("Which of these localities best match my priorities, and what information is still missing?");
 const [budget,setBudget]=useState("");
 const [priorities,setPriorities]=useState<string[]>(["Public transport","Affordable housing"]);
 const [answer,setAnswer]=useState("");
 const [evidence,setEvidence]=useState("");
 const [model,setModel]=useState("");
 const [busy,setBusy]=useState(false);
 const [error,setError]=useState("");
 const available=useMemo(()=>areas.slice(0,40),[areas]);
 async function ask(){
  if(question.trim().length<5){setError("Please enter a question of at least 5 characters.");return}
  if(!available.length){setError("The locality catalogue has not loaded yet.");return}
  setBusy(true);setError("");setAnswer("");
  try{
   const result=await api.aiRecommend({
    question:question.trim(),
    ...(budget.trim()?{budget_inr:Number(budget)}:{}),
    priorities,
    localities:available.map(area=>({name:area.name,city:area.city,description:area.description,indicators:area.indicators}))
   });
   setAnswer(result.answer);setEvidence(result.evidence_note);setModel(result.model);
  }catch(e){setError(e instanceof Error?e.message:"The AI advisor could not complete this request.")}
  finally{setBusy(false)}
 }
 const panel:React.CSSProperties={background:"#fff",border:"1px solid #e5e9e2",borderRadius:16,padding:22,marginTop:18};
 const field:React.CSSProperties={width:"100%",padding:12,border:"1px solid #dce3d8",borderRadius:9,font:"inherit",boxSizing:"border-box"};
 return <section style={panel}>
  <div style={{display:"flex",alignItems:"center",gap:10,marginBottom:8}}><Sparkles color="#648b42"/><div><h2 style={{margin:0}}>AI Locality Advisor</h2><small style={{color:"#66705f"}}>Preference-aware answers grounded in your locality catalogue</small></div></div>
  <p style={{color:"#687166",lineHeight:1.55}}>Tell LocalLens what matters to you. The assistant will use the available locality descriptions and indicator sources, and point out where evidence is missing.</p>
  <label style={{display:"block",fontWeight:600,margin:"16px 0 7px"}}>YOUR QUESTION</label>
  <textarea value={question} onChange={e=>setQuestion(e.target.value)} rows={3} style={field}/>
  <div style={{display:"grid",gridTemplateColumns:"minmax(0,1fr) 2fr",gap:18,marginTop:16}}>
   <label style={{fontWeight:600}}>MONTHLY BUDGET (₹)<input inputMode="numeric" type="number" min="0" max="10000000" value={budget} onChange={e=>setBudget(e.target.value)} placeholder="Optional" style={{...field,display:"block",marginTop:7}}/></label>
   <div><b>YOUR PRIORITIES</b><div style={{display:"flex",flexWrap:"wrap",gap:8,marginTop:9}}>{priorityOptions.map(item=><label key={item} style={{fontSize:13,background:priorities.includes(item)?"#eaf2e4":"#f5f6f3",padding:"7px 10px",borderRadius:20,cursor:"pointer"}}><input type="checkbox" checked={priorities.includes(item)} onChange={e=>setPriorities(old=>e.target.checked?[...old,item]:old.filter(v=>v!==item))}/> {item}</label>)}</div></div>
  </div>
  <div style={{display:"flex",justifyContent:"space-between",alignItems:"center",gap:12,marginTop:18,flexWrap:"wrap"}}><small style={{color:"#727b6e"}}>Context supplied: up to {available.length} catalogue localities</small><button onClick={ask} disabled={busy||!available.length} style={{background:"#527b38",color:"#fff",border:0,borderRadius:9,padding:"11px 16px",fontWeight:700,cursor:"pointer",display:"flex",gap:8,alignItems:"center"}}>{busy?"Thinking…": "Ask LocalLens AI"} <Send size={15}/></button></div>
  {error&&<p role="alert" style={{color:"#a22",background:"#fff1f0",padding:12,borderRadius:8}}>{error}</p>}
  {answer&&<div style={{marginTop:20,background:"#f6f8f3",borderRadius:12,padding:18,whiteSpace:"pre-wrap",lineHeight:1.65}}><div style={{display:"flex",gap:7,alignItems:"center",fontWeight:700,marginBottom:10}}><Sparkles size={16}/> LocalLens AI response</div>{answer}<small style={{display:"block",marginTop:14,color:"#6d7668"}}>Model: {model} · {evidence}</small></div>}
  <div style={{display:"flex",gap:8,alignItems:"flex-start",marginTop:16,color:"#737b70",fontSize:12,lineHeight:1.5}}><Info size={15}/> AI guidance is not a verified safety, rental, financial or transport assessment. Illustrative and community-submitted information may be incomplete or unverified. Confirm important details independently.</div>
 </section>
}
