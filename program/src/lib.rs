use anchor_lang::prelude::*;
use anchor_spl::token::{self, Burn, Mint, Token, TokenAccount, Transfer};

declare_id!("RUGTokenProgramID111111111111111111111111111111");

#[program]
pub mod rug_token {
    use super::*;

    pub fn initialize(
        ctx: Context<Initialize>,
        initial_supply: u64,
        follow_trade_fee: u64,
        burn_rate: u8,
    ) -> Result<()> {
        let token_program = &ctx.program;
        let token_mint = &ctx.accounts.mint;
        let owner = &ctx.accounts.owner;

        // Initialize state
        let state = &mut ctx.accounts.state;
        state.owner = owner.key();
        state.follow_trade_fee = follow_trade_fee;
        state.burn_rate = burn_rate;
        state.trading_system = Pubkey::default();

        // Mint initial supply to owner
        token::mint_to(
            CpiContext::new(
                token_program.to_account_info(),
                token::MintTo {
                    mint: token_mint.to_account_info(),
                    to: owner.to_account_info(),
                    authority: token_mint.to_account_info(),
                },
            ),
            initial_supply,
        )?;

        Ok(())
    }

    pub fn set_trading_system(
        ctx: Context<SetTradingSystem>,
        trading_system: Pubkey,
    ) -> Result<()> {
        require!(trading_system != Pubkey::default(), "Invalid address");
        let state = &mut ctx.accounts.state;
        state.trading_system = trading_system;
        Ok(())
    }

    pub fn pay_follow_trade_fee(ctx: Context<PayFollowTradeFee>) -> Result<()> {
        let state = &ctx.accounts.state;
        let fee = state.follow_trade_fee;
        let burn_amount = (fee * state.burn_rate as u64) / 100;
        let system_amount = fee - burn_amount;

        // Burn tokens
        token::burn(
            CpiContext::new(
                ctx.accounts.token_program.to_account_info(),
                Burn {
                    mint: ctx.accounts.mint.to_account_info(),
                    from: ctx.accounts.user_token_account.to_account_info(),
                    authority: ctx.accounts.user.to_account_info(),
                },
            ),
            burn_amount,
        )?;

        // Transfer to trading system
        token::transfer(
            CpiContext::new(
                ctx.accounts.token_program.to_account_info(),
                Transfer {
                    from: ctx.accounts.user_token_account.to_account_info(),
                    to: ctx.accounts.trading_system_token_account.to_account_info(),
                    authority: ctx.accounts.user.to_account_info(),
                },
            ),
            system_amount,
        )?;

        emit!(FollowTradeFeePaid {
            user: ctx.accounts.user.key(),
            amount: fee,
        });

        Ok(())
    }

    pub fn update_follow_trade_fee(
        ctx: Context<UpdateFollowTradeFee>,
        new_fee: u64,
    ) -> Result<()> {
        let state = &mut ctx.accounts.state;
        state.follow_trade_fee = new_fee;
        Ok(())
    }

    pub fn update_burn_rate(
        ctx: Context<UpdateBurnRate>,
        new_rate: u8,
    ) -> Result<()> {
        require!(new_rate <= 100, "Burn rate cannot exceed 100%");
        let state = &mut ctx.accounts.state;
        state.burn_rate = new_rate;
        Ok(())
    }
}

#[derive(Accounts)]
pub struct Initialize<'info> {
    #[account(init, payer = owner, space = 8 + TokenState::LEN)]
    pub state: Account<'info, TokenState>,
    #[account(mut)]
    pub mint: Account<'info, Mint>,
    #[account(mut)]
    pub owner: Signer<'info>,
    pub system_program: Program<'info, System>,
    pub token_program: Program<'info, Token>,
}

#[derive(Accounts)]
pub struct SetTradingSystem<'info> {
    #[account(mut, has_one = owner)]
    pub state: Account<'info, TokenState>,
    pub owner: Signer<'info>,
}

#[derive(Accounts)]
pub struct PayFollowTradeFee<'info> {
    #[account(mut)]
    pub state: Account<'info, TokenState>,
    #[account(mut)]
    pub mint: Account<'info, Mint>,
    #[account(mut)]
    pub user_token_account: Account<'info, TokenAccount>,
    #[account(mut)]
    pub trading_system_token_account: Account<'info, TokenAccount>,
    pub user: Signer<'info>,
    pub token_program: Program<'info, Token>,
}

#[derive(Accounts)]
pub struct UpdateFollowTradeFee<'info> {
    #[account(mut, has_one = owner)]
    pub state: Account<'info, TokenState>,
    pub owner: Signer<'info>,
}

#[derive(Accounts)]
pub struct UpdateBurnRate<'info> {
    #[account(mut, has_one = owner)]
    pub state: Account<'info, TokenState>,
    pub owner: Signer<'info>,
}

#[account]
pub struct TokenState {
    pub owner: Pubkey,
    pub follow_trade_fee: u64,
    pub burn_rate: u8,
    pub trading_system: Pubkey,
}

impl TokenState {
    pub const LEN: usize = 32 + 8 + 1 + 32;
}

#[event]
pub struct FollowTradeFeePaid {
    pub user: Pubkey,
    pub amount: u64,
}

#[event]
pub struct TokensBurned {
    pub amount: u64,
}