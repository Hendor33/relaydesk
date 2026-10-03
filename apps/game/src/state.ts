import {species,type Kind} from './data';
export type Mon={species:string;level:number;xp:number;hp:number;maxHp:number;pp:number};
export type Save={version:1;starterChosen:boolean;team:Mon[];box:Mon[];balls:number;potions:number;badges:number;defeated:string[];seen:string[];caught:string[];map:string;x:number;y:number;muted:boolean};
export const fresh=():Save=>({version:1,starterChosen:false,team:[],box:[],balls:6,potions:3,badges:0,defeated:[],seen:[],caught:[],map:'town',x:9,y:10,muted:false});
export function makeMon(id:string,level:number):Mon{const s=species[id];const maxHp=s.baseHp+level*2;return{species:id,level,xp:0,hp:maxHp,maxHp,pp:15}}
export function loadSave(storage:Pick<Storage,'getItem'>):Save|null{try{const raw=storage.getItem('prvni-odznak-save');if(!raw)return null;const parsed=JSON.parse(raw) as Partial<Save>;if(parsed.version!==1||!Array.isArray(parsed.team)||typeof parsed.balls!=='number')return null;return parsed as Save}catch{return null}}
export function saveGame(s:Save,storage:Pick<Storage,'setItem'>):boolean{try{storage.setItem('prvni-odznak-save',JSON.stringify(s));return true}catch{return false}}
export function damage(attacker:Kind,level:number,defender:Kind,random=1){const mult=effect(attacker.type,defender.type);return Math.max(1,Math.floor((4+level+attacker.attack*.7)*mult*random))}
export const effect=(from:Kind['type'],to:Kind['type'])=>effectivenessSafe(from,to);
function effectivenessSafe(from:string,to:string){const table:Record<string,Record<string,number>>={tráva:{voda:2,kámen:2,oheň:.5,hmyz:.5},oheň:{tráva:2,hmyz:2,voda:.5,kámen:.5},voda:{oheň:2,kámen:2,tráva:.5},kámen:{oheň:2,hmyz:2},hmyz:{tráva:2,oheň:.5},normální:{kámen:.5}};return table[from]?.[to]??1}
export function captureChance(hp:number,maxHp:number){return Math.min(.9,.22+(1-hp/maxHp)*.65)}
