import {useEffect,useRef,useState} from 'react';
import * as maplibregl from 'maplibre-gl';
import workerUrl from 'maplibre-gl/dist/maplibre-gl-worker.mjs?worker&url';
import 'maplibre-gl/dist/maplibre-gl.css';
maplibregl.setWorkerUrl(workerUrl);

export default function MapView(){
  const container=useRef<HTMLDivElement>(null);
  const instance=useRef<maplibregl.Map|null>(null);
  const [showStreets,setShowStreets]=useState(true);
  const [ready,setReady]=useState(false);
  const [rendered,setRendered]=useState(false);
  const [error,setError]=useState('');
  useEffect(()=>{
    if(!container.current)return;
    let map:maplibregl.Map;
    try{
      map=new maplibregl.Map({container:container.current,center:[51.410,35.698],zoom:15.2,attributionControl:false,style:import.meta.env.VITE_MAP_STYLE_URL||{version:8,sources:{},layers:[{id:'background',type:'background',paint:{'background-color':'#e9eee9'}}]}});
      instance.current=map;
      map.addControl(new maplibregl.NavigationControl({showCompass:true}),'top-left');
      map.addControl(new maplibregl.ScaleControl({unit:'metric'}),'bottom-left');
      map.addControl(new maplibregl.AttributionControl({compact:false,customAttribution:'© <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noreferrer">OpenStreetMap contributors</a> · ODbL'}),'bottom-right');
      map.on('load',async()=>{
        try{
          const response=await fetch('/data/walking-preview.geojson');
          if(!response.ok)throw Error('داده معابر در دسترس نیست.');
          const data=await response.json();
          if(!data.features?.length)throw Error('داده معابر خالی است.');
          if(instance.current!==map)return;
          map.addSource('walking',{type:'geojson',data});
          map.addLayer({id:'walking-lines',type:'line',source:'walking',paint:{'line-color':'#167875','line-width':['interpolate',['linear'],['zoom'],12,1.2,17,5],'line-opacity':.85}});
          const bounds=new maplibregl.LngLatBounds();
          for(const f of data.features)for(const c of f.geometry.coordinates)bounds.extend(c);
          map.fitBounds(bounds,{padding:40,maxZoom:16,duration:0});
          setReady(true);
        }catch(e){setError(e instanceof Error?e.message:'دریافت داده ناموفق بود.');}
      });
      map.on('idle',()=>{if(instance.current===map&&map.getLayer('walking-lines')&&map.isSourceLoaded('walking')&&map.queryRenderedFeatures({layers:['walking-lines']}).length>0)setRendered(true);});
      map.on('error',(event)=>{if(instance.current!==map)return;console.error('Map renderer:',event.error);setError('نمایش نقشه یا نقشه زمینه با خطا روبه‌رو شد؛ گزارش متنی در دسترس است.');});
    }catch(event){console.error('Map initialization:',event);setError('نمایش نقشه به WebGL نیاز دارد. گزارش متنی همین بخش در دسترس است.');}
    return()=>{instance.current=null;map?.remove();};
  },[]);
  useEffect(()=>{if(ready&&instance.current?.getLayer('walking-lines'))instance.current.setLayoutProperty('walking-lines','visibility',showStreets?'visible':'none');},[ready,showStreets]);
  return <div className="map-layout">
    <div className="map-frame"><div ref={container} className="map" role="region" aria-label="نقشه جغرافیایی محدوده آزمایشی معابر مرکز تهران" data-rendered-streets={rendered} tabIndex={0}/><span className="map-caption">محدوده کوچک اعتبارسنجی · شبکه مرجع ۲۰۲۶</span>{error&&<div className="map-error" role="status">{error}</div>}</div>
    <aside className="map-controls" aria-label="لایه‌های نقشه">
      <span className="eyebrow">آنچه روی نقشه می‌بینید</span><h3>معابر واقعی، در مقیاس آزمایشی</h3>
      <p>هندسه معابر از OpenStreetMap دریافت شده است. این نقشه فقط محدوده کوچک آزمون شبکه را نشان می‌دهد؛ سنجه دسترسی آگهی‌ها نیست.</p>
      <label className="layer"><input type="checkbox" checked={showStreets} onChange={e=>setShowStreets(e.target.checked)}/><span className="line-key"/>معابر محدوده آزمایشی</label>
      <label className="layer disabled"><input type="checkbox" disabled/>ایستگاه‌ها و خطوط مترو <small>در انتظار اعتبارسنجی</small></label>
      <label className="layer disabled"><input type="checkbox" disabled/>نقشه قیمت‌های تجمیع‌شده <small>در انتظار تأیید پوشش جغرافیایی</small></label>
      <p className="small">برای جابه‌جایی از کلیدهای جهت‌نما و برای بزرگ‌نمایی از + و − استفاده کنید. نقشه زمینه خارجی پیش‌فرض بارگیری نمی‌شود.</p>
      <a href="/data/network-validation.json">گزارش پوشش و آزمون مسیرها ↗</a>
    </aside>
  </div>;
}
