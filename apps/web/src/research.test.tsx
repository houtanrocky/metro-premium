import React from 'react';
import {readFileSync} from 'node:fs';
import {describe,it,expect,vi} from 'vitest';
import {render,screen,fireEvent} from '@testing-library/react';
import {fa,validateResearch} from './data';
import {shortestPath} from './NetworkLesson';
import App from './App';
const payload=JSON.parse(readFileSync('data/public/research.json','utf8'));
vi.mock('./MapView',()=>({default:()=> <div>نقشه آزمایشی معابر</div>}));

describe('Publication boundaries',()=>{
  it('accepts actual audit aggregates, rejects synthetic and unverified price claims',()=>{
    expect(validateResearch(payload).scope.source_rows).toBe(1000000);
    expect(()=>validateResearch({...payload,kind:'synthetic_demo'})).toThrow();
    expect(()=>validateResearch({...payload,findings_available:true})).toThrow();
    expect(()=>validateResearch({...payload,months:[{month:'bad',n:4}]})).toThrow();
    expect(()=>validateResearch({...payload,neighborhoods:[{n:1}]})).toThrow();
  });
  it('shows real counts and filters with honest missing measures',async()=>{
    vi.stubGlobal('fetch',vi.fn().mockResolvedValue({ok:true,json:async()=>payload}));
    render(<App/>);
    expect(await screen.findByRole('heading',{level:1})).toHaveTextContent('خونه نزدیک مترو');
    expect(screen.getAllByText(fa(payload.scope.analysis_rows)).length).toBeGreaterThan(0);
    fireEvent.change(screen.getByLabelText('نمایش'),{target:{value:'radius'}});
    expect(screen.getAllByText('شعاع نامشخص').length).toBeGreaterThan(0);
    const selected=payload.neighborhoods[0].neighborhood;
    fireEvent.change(screen.getByLabelText('انتخاب محله'),{target:{value:selected}});
    expect(screen.getByText('تأیید نشده')).toBeInTheDocument();
    expect(screen.getByRole('link',{name:'داده رسمی دیوار ↗'})).toHaveAttribute('href',payload.source.url);
  });
  it('fails visibly on network error without showing invented fallback',async()=>{
    vi.stubGlobal('fetch',vi.fn().mockRejectedValue(new Error('offline')));
    render(<App/>);
    expect(await screen.findByRole('alert')).toHaveTextContent('offline');
    expect(screen.getByRole('button',{name:'تلاش دوباره'})).toBeInTheDocument();
  });
});
describe('Interactive network lesson',()=>{
  it('changes shortest distance when a link closes and detects disconnection',()=>{
    const edges:[string,string,number][]=[['A','B',130],['B','C',100],['C','D',160],['D','E',100],['B','E',160]];
    expect(shortestPath(edges,'A','E')?.distance).toBe(290);
    expect(shortestPath(edges.slice(0,-1),'A','E')?.distance).toBe(490);
    expect(shortestPath([],'A','E')).toBeNull();
  });
});
