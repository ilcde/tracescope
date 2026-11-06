import {defineConfig} from 'vite';
import react from '@vitejs/plugin-react';
export default defineConfig({plugins:[react()],base:'./',server:{proxy:{'/api':'http://127.0.0.1:7432'}},build:{chunkSizeWarningLimit:1600},worker:{format:'es'}});
