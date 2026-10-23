import {defineConfig} from 'vite';
import react from '@vitejs/plugin-react';
import fa from './src/locales/fa.json';
export default defineConfig({base:process.env.VITE_BASE_PATH||'/',plugins:[react(),{name:'localized-html',transformIndexHtml(html){return html.replace('__TITLE__',fa['meta.title']).replace('__DESCRIPTION__',fa['meta.description']);}}],server:{port:5173,strictPort:true},build:{chunkSizeWarningLimit:700}});
