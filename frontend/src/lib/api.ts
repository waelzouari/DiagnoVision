import axios, { AxiosError, type InternalAxiosRequestConfig } from 'axios';
let csrf: string | null=null; let refreshing: Promise<void>|null=null;
export const api=axios.create({baseURL:'/api/v1',withCredentials:true,headers:{Accept:'application/json'}});
export async function ensureCsrf(){if(!csrf){const {data}=await api.get<{csrf_token:string}>('/auth/csrf');csrf=data.csrf_token;}return csrf;}
api.interceptors.request.use(async (config:InternalAxiosRequestConfig)=>{const method=config.method?.toLowerCase();const csrfExempt=config.url==='/auth/login'||config.url==='/auth/refresh';if(method&&!['get','head','options'].includes(method)&&!csrfExempt){config.headers['X-CSRF-Token']=await ensureCsrf();}return config;});
api.interceptors.response.use(r=>r,async(error:AxiosError)=>{const original=error.config as (InternalAxiosRequestConfig&{_retry?:boolean})|undefined;if(error.response?.status===401&&original&&!original._retry&&!original.url?.includes('/auth/')){original._retry=true;refreshing??=api.post('/auth/refresh').then(()=>{}).finally(()=>{refreshing=null});await refreshing;return api(original);}throw error;});
export function clearSession(){csrf=null;}
export const errorMessage=(e:unknown)=>axios.isAxiosError(e)?String(e.response?.data?.detail??e.message):e instanceof Error?e.message:'Something went wrong';
