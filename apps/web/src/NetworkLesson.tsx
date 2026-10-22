import {useMemo,useState} from 'react';
import {fa} from './data';
type Edge=[string,string,number];
const nodes:Record<string,[number,number]>={A:[75,150],B:[205,150],C:[205,50],D:[365,50],E:[365,150]};
export function shortestPath(edges:Edge[],start:string,target:string){
  const costs:Record<string,number>={[start]:0},previous:Record<string,string>={},visited=new Set<string>();
  while(true){
    const next=Object.keys(costs).filter(n=>!visited.has(n)).sort((a,b)=>costs[a]-costs[b])[0];
    if(!next)break;
    if(next===target){const path=[target];while(path[0]!==start)path.unshift(previous[path[0]]);return {distance:costs[target],path};}
    visited.add(next);
    for(const [a,b,w] of edges){const neighbor=a===next?b:b===next?a:null;if(neighbor&&costs[next]+w<(costs[neighbor]??Infinity)){costs[neighbor]=costs[next]+w;previous[neighbor]=next;}}
  }
  return null;
}
export default function NetworkLesson(){
  const [blocked,setBlocked]=useState(false);
  const edges:Edge[]=useMemo(()=>[['A','B',130],['B','C',100],['C','D',160],['D','E',100],...(!blocked?[['B','E',160] as Edge]:[])],[blocked]);
  const route=shortestPath(edges,'A','E')!;
  return <div className="lesson"><div><span className="eyebrow">یک آزمایش کوچک · کاملاً ساختگی</span><h3>دیوارها فاصله را عوض می‌کنند.</h3><p>گره‌ها محل اتصال مسیرها هستند و یال‌ها راه‌های قابل عبور. کوتاه‌ترین مسیر، کمترین مجموع طول یال‌هاست. یک مانع می‌تواند مسیر پیاده را طولانی‌تر کند، حتی وقتی فاصله مستقیم تغییری نکرده است.</p><button className="button outline" aria-pressed={blocked} onClick={()=>setBlocked(v=>!v)}>{blocked?'باز کردن مسیر میانی':'بستن مسیر میانی'}</button><p className="small">این مثال، نقشه تهران یا نتیجه پژوهش نیست. طول یال‌ها بر حسب متر فرضی است.</p></div><div className="lesson-visual"><svg viewBox="0 0 440 210" role="img" aria-label={`مثال ساختگی: فاصله مستقیم ۲۹۰ متر؛ مسیر پیاده ${fa(route.distance)} متر`}>
    <line x1="75" y1="150" x2="365" y2="150" stroke="#88969c" strokeDasharray="4 6"/>
    {edges.map(([a,b,w])=>{const active=route.path.some((n,i)=>n===a&&route.path[i+1]===b||n===b&&route.path[i+1]===a);return <g key={a+b}><line x1={nodes[a][0]} y1={nodes[a][1]} x2={nodes[b][0]} y2={nodes[b][1]} stroke={active?'#167875':'#ced5d2'} strokeWidth="5"/><text x={(nodes[a][0]+nodes[b][0])/2} y={(nodes[a][1]+nodes[b][1])/2-12} textAnchor="middle">{fa(w)}</text></g>;})}
    {Object.entries(nodes).map(([id,[x,y]])=><g key={id}><circle cx={x} cy={y} r="9" fill="#f7f5ef" stroke="#183342" strokeWidth="3"/><text x={x} y={y+30} textAnchor="middle">{id==='A'?'خانه فرضی':id==='E'?'ورودی فرضی':id}</text></g>)}
    </svg><div className="lesson-values"><span>فاصله مستقیم <strong>{fa(290)} متر</strong></span><span>مسیر شبکه <strong>{fa(route.distance)} متر</strong></span><span>نسبت دو فاصله <strong>{fa(route.distance/290,2)}</strong></span></div></div></div>;
}
