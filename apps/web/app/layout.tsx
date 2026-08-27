import "./globals.css"; import { Shell } from "@/components/shell";
export const metadata={title:"RelayDesk",description:"Personal automation, executed locally"};
export default function Layout({children}:{children:React.ReactNode}){return <html lang="en"><body><Shell>{children}</Shell></body></html>}
