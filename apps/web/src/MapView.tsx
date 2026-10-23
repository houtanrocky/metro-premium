import {useEffect,useRef,useState} from 'react';
import * as maplibregl from 'maplibre-gl';
import workerUrl from 'maplibre-gl/dist/maplibre-gl-worker.mjs?worker&url';
import {asset} from './assets';
import {useLocale} from './i18n';
import 'maplibre-gl/dist/maplibre-gl.css';
maplibregl.setWorkerUrl(workerUrl);
export default function MapView(){
  const {t,language}=useLocale();
  const container=useRef<HTMLDivElement>(null),instance=useRef<maplibregl.Map|null>(null);
  const visible=useRef(true);
  const [showStreets,setShowStreets]=useState(true),[rendered,setRendered]=useState(false),[error,setError]=useState('');
  useEffect(()=>{
    if(!container.current)return;
    const abort=new AbortController();let map:maplibregl.Map;
    setRendered(false);setError('');
    try{
      map=new maplibregl.Map({container:container.current,center:[51.410,35.698],zoom:15.2,attributionControl:false,
        locale:{'NavigationControl.ZoomIn':t('map.zoomIn'),'NavigationControl.ZoomOut':t('map.zoomOut'),'NavigationControl.ResetBearing':t('map.compass'),'AttributionControl.ToggleAttribution':t('map.attribution'),'Map.Title':t('map.map'),'ScaleControl.Meters':t('map.meters'),'ScaleControl.Kilometers':t('map.kilometers')},
        style:import.meta.env.VITE_MAP_STYLE_URL||{version:8,sources:{},layers:[{id:'background',type:'background',paint:{'background-color':'#e9eee9'}}]}});
      instance.current=map;
      map.addControl(new maplibregl.NavigationControl({showCompass:true}),'top-left');
      map.addControl(new maplibregl.ScaleControl({unit:'metric'}),'bottom-left');
      map.addControl(new maplibregl.AttributionControl({compact:false,customAttribution:`© <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noreferrer">${t('map.contributors')}</a> · ODbL`}), 'bottom-right');
      map.on('load',async()=>{
        try{
          const response=await fetch(asset('data/walking-preview.geojson'),{signal:abort.signal});
          if(!response.ok)throw Error();
          const data=await response.json();if(!data.features?.length)throw Error();
          if(instance.current!==map)return;
          map.addSource('walking',{type:'geojson',data});
          map.addLayer({id:'walking-lines',type:'line',source:'walking',layout:{visibility:visible.current?'visible':'none'},paint:{'line-color':'#167875','line-width':['interpolate',['linear'],['zoom'],12,1.2,17,5],'line-opacity':.85}});
          const bounds=new maplibregl.LngLatBounds();for(const f of data.features)for(const c of f.geometry.coordinates)bounds.extend(c);
          map.fitBounds(bounds,{padding:40,maxZoom:16,duration:0});
        }catch(e){if(instance.current===map&&!abort.signal.aborted)setError('map.errorData');}
      });
      map.on('idle',()=>{if(instance.current===map&&map.getLayer('walking-lines')&&map.isSourceLoaded('walking')&&map.queryRenderedFeatures({layers:['walking-lines']}).length>0)setRendered(true);});
      map.on('error',()=>{if(instance.current===map)setError('map.errorRender');});
    }catch{setError('map.errorWebgl');}
    return()=>{abort.abort();instance.current=null;map?.remove();};
  },[language,t]);
  useEffect(()=>{visible.current=showStreets;if(instance.current?.getLayer('walking-lines'))instance.current.setLayoutProperty('walking-lines','visibility',showStreets?'visible':'none');},[showStreets]);
  return <div className="map-layout"><div className="map-frame"><div ref={container} className="map" role="region" aria-label={t('map.aria')} data-rendered-streets={rendered} tabIndex={0}/><span className="map-caption">{t('map.caption')}</span>{error&&<div className="map-error" role="status">{t(error)}</div>}</div>
  <aside className="map-controls" aria-label={t('map.layers')}><span className="eyebrow">{t('map.eyebrow')}</span><h3>{t('map.streetsTitle')}</h3><p>{t('map.explanation')}</p><label className="layer"><input type="checkbox" checked={showStreets} onChange={e=>setShowStreets(e.target.checked)}/><span className="line-key"/>{t('map.streets')}</label><label className="layer disabled"><input type="checkbox" disabled/>{t('map.metro')}<small>{t('map.waiting')}</small></label><label className="layer disabled"><input type="checkbox" disabled/>{t('map.prices')}<small>{t('map.coverageWaiting')}</small></label><p className="small">{t('map.keyboard')}</p><a href={asset('data/network-validation.json')}>{t('map.report')}</a></aside></div>;
}
