import { StackHandler } from "@stackframe/stack";
import { stackClientApp } from "./client";

export default function Handler() {
  return <StackHandler fullPage app={stackClientApp} />;
}
