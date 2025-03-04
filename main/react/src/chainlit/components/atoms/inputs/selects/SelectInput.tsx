import { MouseEvent, useState } from "react";
import { grey } from "chainlit/theme/index";

import KeyboardArrowDown from "@mui/icons-material/KeyboardArrowDown";
import { Stack, type SxProps } from "@mui/material";
import MSelect, { SelectChangeEvent, SelectProps } from "@mui/material/Select";

import { InputStateHandler } from "chainlit/components/atoms/inputs/InputStateHandler";

import { useIsDarkMode } from "chainlit/hooks/useIsDarkMode";

import { IInput } from "chainlit/types/Input";

import { MenuItem } from "./MenuItem";

type SelectItem = {
  label: string;
  icon?: JSX.Element;
  notificationCount?: number;
  value: string | number;
};

type SelectInputProps = IInput &
  Omit<SelectProps<string>, "value" | "onChange"> & {
    children?: React.ReactNode;
    items?: SelectItem[];
    name?: string;
    onChange: (e: SelectChangeEvent) => void;
    placeholder?: string;
    renderLabel?: () => string;
    onItemMouseEnter?: (e: MouseEvent<HTMLLIElement>, itemName: string) => void;
    onItemMouseLeave?: (e: MouseEvent<HTMLLIElement>) => void;
    value?: string | number;
    iconSx?: SxProps;
  };

const SelectInput = ({
  children,
  description,
  disabled = false,
  hasError,
  id,
  items,
  label,
  name,
  onChange,
  onItemMouseEnter,
  onItemMouseLeave,
  size = "small",
  tooltip,
  value,
  placeholder = "Select",
  renderLabel,
  onClose,
  sx,
  iconSx,
  ...rest
}: SelectInputProps): JSX.Element => {
  const isDarkMode = useIsDarkMode();

  const [menuOpen, setMenuOpen] = useState(false);

  const handleMenuOpen = () => {
    setMenuOpen(true);
  };

  const handleMenuClose = (event: React.SyntheticEvent) => {
    setMenuOpen(false);

    if (onClose) {
      onClose(event);
    }
  };

  return (
    <InputStateHandler
      id={id}
      hasError={hasError}
      description={description}
      label={label}
      tooltip={tooltip}
      sx={sx}
    >
      <MSelect
        {...rest}
        size={size}
        onClose={handleMenuClose}
        onOpen={handleMenuOpen}
        labelId={id}
        value={value?.toString()}
        onChange={onChange}
        disabled={disabled}
        displayEmpty
        renderValue={() => {
          const item = items?.find((item) => item.value === value);
          if (!value || value === "") return placeholder;
          return (
            (renderLabel && renderLabel()) || (
              <Stack direction="row" alignItems="center" spacing={1}>
                {item?.icon}
                <span>{item?.label}</span>
              </Stack>
            )
          );
        }}
        sx={{
          backgroundColor: (theme) => theme.palette.background.paper,
          borderRadius: 1,
          "&.MuiOutlinedInput-root": {
            "& fieldset": {
              border: (theme) => `1px solid ${theme.palette.divider}`,
            },
          },
        }}
        inputProps={{
          id: id,
          name: name || id,
          sx: {
            color: "text.primary",
            fontSize: "14px",
            fontWeight: 400,
          },
        }}
        MenuProps={{
          PaperProps: {
            sx: {
              border: (theme: any) => `1px solid ${theme.palette.divider}`,
              boxShadow: (theme: any) =>
                theme.palette.mode === "light"
                  ? "0px 2px 4px 0px #0000000D"
                  : "0px 10px 10px 0px #0000000D",
              "&& .Mui-selected, .Mui-selected.Mui-selected:hover": {
                backgroundColor: isDarkMode ? grey[800] : "primary.light",
              },
            },
          },
          MenuListProps: {
            sx: { backgroundColor: isDarkMode ? grey[900] : "" },
          },
        }}
        IconComponent={(props) => (
          <KeyboardArrowDown
            {...props}
            fontSize="16px"
            sx={{
              px: "9px",
              color: !disabled
                ? `${isDarkMode ? grey[300] : grey[600]} !important`
                : "",
              ...iconSx,
            }}
          />
        )}
      >
        {children ||
          items?.map((item) => (
            <MenuItem
              isDarkMode={isDarkMode}
              data-test={`select-item:${item.label}`}
              onMouseEnter={(e) =>
                menuOpen && onItemMouseEnter?.(e, item.label)
              }
              onMouseLeave={(e) => menuOpen && onItemMouseLeave?.(e)}
              item={item}
              selected={item.value === value}
              key={item.value}
              value={item.value}
            />
          ))}
      </MSelect>
    </InputStateHandler>
  );
};

export { SelectInput };
export type { SelectItem, SelectInputProps };
