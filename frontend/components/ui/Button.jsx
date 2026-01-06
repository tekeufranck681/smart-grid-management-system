import { forwardRef } from "react";
import { cn } from "@/lib/cn";

const Button = forwardRef(function Button(
  { className, variant = "primary", size = "md", ...props },
  ref
) {
  return (
    <button
      ref={ref}
      className={cn(
        "inline-flex items-center justify-center rounded-md font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-ring",
        {
          primary:
            "bg-primary text-primary-foreground hover:bg-primary/90",
          secondary:
            "bg-secondary text-secondary-foreground hover:bg-secondary/80",
          ghost:
            "text-muted-foreground hover:text-foreground hover:bg-muted",
        }[variant],
        {
          sm: "h-9 px-3 text-sm",
          md: "h-10 px-4 text-sm",
          lg: "h-12 px-6 text-base",
        }[size],
        className
      )}
      {...props}
    />
  );
});

export default Button;
