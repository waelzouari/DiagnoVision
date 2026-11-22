import { clsx, type ClassValue } from 'clsx'; import { twMerge } from 'tailwind-merge';
export const cn=(...v:ClassValue[])=>twMerge(clsx(v));
export const formatDate=(v?:string)=>v?new Intl.DateTimeFormat(undefined,{dateStyle:'medium'}).format(new Date(v)):'—';
export const initials=(name='')=>name.split(/\s+/).map(x=>x[0]).slice(0,2).join('').toUpperCase();
